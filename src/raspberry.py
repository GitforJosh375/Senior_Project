import threading
import time
import requests
from picamera import PiCamera
from flask import Flask, request, jsonify

# Setup camera
camera = PiCamera()

# Flask server for listening to incoming POST requests
app = Flask(__name__)

# URL of the web server to send images
upload_url = 'http://<your_pc_ip>:5000/upload'  # Replace <your_pc_ip> with the server's IP

# Global variable to control camera capture
capture_images = False  # Initially set to False to prevent capturing

def capture_and_send_image():
    global capture_images  # Access the global variable
    while True:
        if not capture_images:  # Check if capturing should be stopped
            print("Camera capture is paused.")
            time.sleep(1)  # Sleep to avoid busy waiting
            continue  # Skip to the next loop iteration if capturing is paused

        # Capture image
        image_path = '/home/pi/captured_image.jpg'
        camera.capture(image_path)
        print("Image captured!")

        # Send image to the web server
        with open(image_path, 'rb') as img_file:
            files = {'file': img_file}
            response = requests.post(upload_url, files=files)

        if response.status_code == 200:
            # Process the JSON response from the server
            response_data = response.json()
            car_count = response_data.get('car_count', 0)  # Get the car count
            print(f"Image sent successfully! Car count: {car_count}")
        else:
            print("Failed to send image, status code:", response.status_code)

        # Capture image every 10 seconds (adjust as needed)
        time.sleep(10)

@app.route('/command', methods=['POST'])
def handle_command():
    global capture_images  # Access the global variable
    data = request.json
    if not data:
        return jsonify({'message': 'No data received'}), 400

    command = data.get('command')
    if command == 'stop':
        capture_images = False  # Stop capturing images
        print("Received stop command.")
    elif command == 'start':
        capture_images = True  # Start capturing images
        print("Received start command.")
    else:
        print(f"Unknown command received: {command}")

    return jsonify({'message': 'Command executed'}), 200

# Use threading to run Flask server and camera capture simultaneously
if __name__ == "__main__":

    # Run the image capture and upload task
    capture_and_send_image()
