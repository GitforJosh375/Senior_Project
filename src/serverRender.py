import requests
import cv2
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO  # Make sure you have ultralytics installed

app = Flask(__name__)

# Initialize YOLOv8 model
model = YOLO("yolov8n.pt")  # Use the appropriate YOLOv8 model

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        # Read the image directly from the uploaded file without saving it
        image_bytes = file.read()
        np_array = np.frombuffer(image_bytes, np.uint8)  # Convert to numpy array
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # Decode the image

        # Run YOLOv8 inference
        results = model(img)

        # Initialize a counter for the number of cars detected
        car_count = 0
        for result in results:
            for box in result.boxes:
                class_index = int(box.cls)
                class_name = model.names[class_index]
                if class_name == 'car':
                    car_count += 1

        print(f"Number of cars detected: {car_count}")
        

        # Send a POST request to update car count on the remote server
        detection_url = 'https://sw-server-bgez.onrender.com'  # Replace with your server's IP address
        detection_data = {'count': car_count}
        
        try:
            # Send the car count as a POST request
            detection_response = requests.post(detection_url, json=detection_data)
            
            # Check if the request was successful
            if detection_response.status_code == 200:
                print(f"Car count successfully updated on the server: {detection_response.json()}")
            else:
                print(f"Failed to update car count. Status code: {detection_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending POST request to /detection: {e}")

        # Return a simple response that the image was processed and car count updated
        return jsonify({'car_count': car_count, 'message': 'Detection complete'}), 200


if __name__ == '__main__':
    app.run(debug=True)

