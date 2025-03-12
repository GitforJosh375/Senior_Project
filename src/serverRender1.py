import requests
import cv2
import numpy as np
import os
from flask import Flask, request, jsonify
from ultralytics import YOLO  
import time

app = Flask(__name__)

# Initialize YOLOv8 model once to save memory
model = YOLO("yolov8n.pt")  

@app.route('/')
def home():
    return 'Welcome to the Car Detection API! Use /upload to send images.'


@app.route('/upload', methods=['POST'])
def upload_image():
    start_time = time.time()
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    image_bytes = file.read()
    print(f"Read file: {time.time() - start_time:.2f}s")
    
    np_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    print(f"Decode image: {time.time() - start_time:.2f}s")
    
    img = cv2.resize(img, (416, 416))
    print(f"Resize image: {time.time() - start_time:.2f}s")
    
    results = model.predict(img, device='cpu', half=True)
    print(f"YOLO inference: {time.time() - start_time:.2f}s")
    
    car_count = sum(
        1 for result in results for box in result.boxes
        if model.names[int(box.cls)] == 'car'
    )
    print(f"Count cars: {time.time() - start_time:.2f}s")
    
    detection_url = 'https://sw-server-bgez.onrender.com/detection/detection'
    detection_data = {'count': car_count}
    try:
        detection_response = requests.post(detection_url, json=detection_data, timeout=10)
        print(f"POST request: {time.time() - start_time:.2f}s")
    except requests.exceptions.RequestException as e:
        print(f"POST error: {e}")
    
    del img, np_array, results
    return jsonify({'count': car_count}), 200

        # Send the car count to the remote server
        #detection_url = 'https://sw-server-bgez.onrender.com/detection/detection'
        #detection_data = {'count': car_count}

       # try:
            #detection_response = requests.post(detection_url, json=detection_data)
           # print(f"Server Response: {detection_response.status_code}")
        #except requests.exceptions.RequestException as e:
            #print(f"Error sending POST request: {e}")


