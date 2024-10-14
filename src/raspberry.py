import threading
import time
import requests
from picamera import PiCamera
from flask import Flask, request, jsonify
import RPi.GPIO as GPIO

# Setup camera
camera = PiCamera()

# Setup GPIO pins for LEDs
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for different parking status LEDs
LED_PINS = {
    'full': 17,         # Red LED for all spots filled
    'ten_or_less': 27,  # Yellow LED for 10 or fewer spots available
    'more_than_ten': 22  # Green LED for more than 10 spots available
}

# Function to setup GPIO pins
def setup_gpio():
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Set initial state to LOW (off)

# Flask server for listening to incoming POST requests
app = Flask(__name__)

# URL of the web server to send images
upload_url = 'http://<your_pc_ip>:5000/upload'  # Replace <your_pc_ip> with the server's IP

# Global variable to control camera capture
capture_images = False  # Initially set to False to prevent capturing

def energize_leds(car_count):
    # Turn off all LEDs first
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    # Energize the corresponding LED based on the car count
    if car_count == 0:  # All spots filled
        GPIO.output(LED_PINS['full'], GPIO.HIGH)
    elif car_count <= 10:  # 10 or fewer spots available
        GPIO.output(LED_PINS['ten_or_less'], GPIO.HIGH)
    else:  # More than 10 spots available
        GPIO.output(LED_PINS['more_than_ten'], GPIO.HIGH)

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

            # Energize LEDs based on the car count
            energize_leds(car_count)
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
        GPIO.cleanup()  # Clean up GPIO settings
        print("Received stop command.")
    elif command == 'start':
        setup_gpio()  # Reinitialize GPIO pins
        capture_images = True  # Start capturing images
        print("Received start command.")
    else:
        print(f"Unknown command received: {command}")

    return jsonify({'message': 'Command executed'}), 200

# Use threading to run Flask server and camera capture simultaneously
if __name__ == "__main__":
    setup_gpio()  # Initialize GPIO pins at startup
    try:
        # Run the image capture and upload task
        capture_and_send_image()
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()  # Clean up GPIO settings on exit
