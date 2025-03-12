import requests
import cv2
import numpy as np
import os
from flask import Flask, request, jsonify
from ultralytics import YOLO  

app = Flask(__name__)

# Initialize YOLOv8 model once to save memory
model = YOLO("yolov8n.pt")  

@app.route('/')
def home():
    return 'Welcome to the Car Detection API! Use /upload to send images.'

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        # Read the image
        image_bytes = file.read()
        np_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Resize to save memory
        img = cv2.resize(img, (416, 416))  

        # Run YOLOv8 inference using optimized method
        results = model.predict(img, device='cpu', half=True)  

        # Count cars
        car_count = sum(
            1 for result in results for box in result.boxes
            if model.names[int(box.cls)] == 'car'
        )

        print(f"Number of cars detected: {car_count}")

        # Send the car count to the remote server
        #detection_url = 'https://sw-server-bgez.onrender.com/detection/detection'
        #detection_data = {'count': car_count}

       # try:
            #detection_response = requests.post(detection_url, json=detection_data)
           # print(f"Server Response: {detection_response.status_code}")
        #except requests.exceptions.RequestException as e:
            #print(f"Error sending POST request: {e}")

        # Free memory
        del img, np_array, results  

        return jsonify({'count': car_count}), 200
