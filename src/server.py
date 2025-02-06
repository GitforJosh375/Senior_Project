from flask import Flask, request, jsonify
import os
from ultralytics import YOLO
import cv2
import requests

app = Flask(__name__)

# Define the folder to store images
UPLOAD_FOLDER = './uploads'  # Change this to your desired path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        # Save the uploaded image to a path
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)
        print(f"Image saved at: {image_path}")

        # Load the image using OpenCV
        img = cv2.imread(image_path)

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
        detection_url = 'http://67.43.244.153:3001/detection'  # Replace with your server's IP address
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
        return jsonify({'message': 'Image processed and car count updated successfully', 'car_count': car_count})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
