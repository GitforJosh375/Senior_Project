import psutil
import os
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

def log_memory():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory usage: {mem:.2f} MB")

print("Starting app...")
log_memory()

model = YOLO("yolov8n.pt")
print("Model loaded")
log_memory()

@app.route('/')
def home():
    log_memory()
    return 'Welcome to the Car Detection API! Use /upload to send images.'

@app.route('/upload', methods=['POST'])
def upload_image():
    log_memory()
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Limit file size to 2MB
    image_bytes = file.read()
    if len(image_bytes) > 2 * 1024 * 1024:
        return jsonify({'message': 'File too large, max 2MB'}), 400
    log_memory()

    np_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    log_memory()

    img = cv2.resize(img, (416, 416))
    log_memory()

    results = model.predict(img, device='cpu', half=True)
    log_memory()

    car_count = sum(
        1 for result in results for box in result.boxes
        if model.names[int(box.cls)] == 'car'
    )
    print(f"Number of cars detected: {car_count}")
    log_memory()

    detection_url = 'https://sw-server-bgez.onrender.com/detection/detection'
    detection_data = {'count': car_count}
    try:
        detection_response = requests.post(detection_url, json=detection_data, timeout=10)
        print(f"Server Response: {detection_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")
    log_memory()

    del img, np_array, results
    log_memory()

    return jsonify({'count': car_count}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))