import threading
import time
import requests
from picamera import PiCamera
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

# Server URL for fetching commands and uploading images
server_command_url = 'http://67.43.244.153:3001/command'  # Replace <your_server_ip>
upload_url = 'http://67.43.244.153:5000/upload'           # Replace <your_server_ip>

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
            message = response_data.get('message', 'No message')
            car_count = response_data.get('car_count', 0)  # Get the car count
            print(f"Message from server: {message}")
            print(f"Car count: {car_count}")

            # Energize LEDs based on the car count
            energize_leds(car_count)
        else:
            print("Failed to send image, status code:", response.status_code)

        # Capture image every 20 seconds (adjust as needed)
        time.sleep(20)

def fetch_server_commands():
    global capture_images  # Access the global variable
    while True:
        try:
            # Poll the server for commands
            response = requests.get(server_command_url)
            if response.status_code == 200:
                data = response.json()
                command = data.get('command')

                if command == 'start':
                    setup_gpio()  # Reinitialize GPIO pins
                    capture_images = True
                    print("Received start command.")
                elif command == 'stop':
                    capture_images = False
                    GPIO.cleanup()  # Clean up GPIO settings
                    print("Received stop command.")
                else:
                    print(f"Unknown command received: {command}")
            else:
                print(f"Failed to fetch command, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching command: {e}")

        # Poll every 5 seconds (adjust as needed)
        time.sleep(5)

if __name__ == "__main__":
    setup_gpio()  # Initialize GPIO pins at startup
    try:
        # Start threads for polling server commands and capturing images
        threading.Thread(target=fetch_server_commands, daemon=True).start()
        capture_and_send_image()
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()  # Clean up GPIO settings on exit
