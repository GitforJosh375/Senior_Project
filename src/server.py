from flask import Flask, request, jsonify, send_file
import os
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io

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

        # Visualize the detections on the image
        annotated_img = results[0].plot()

        # Convert the OpenCV image (numpy array) to a PIL image for sending as a response
        pil_img = Image.fromarray(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))

        # Save the image into a BytesIO object (in-memory buffer)
        img_io = io.BytesIO()
        pil_img.save(img_io, 'JPEG')
        img_io.seek(0)

        # Send the image back to the client
        return send_file(img_io, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
