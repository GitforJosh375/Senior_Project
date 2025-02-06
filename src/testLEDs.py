import RPi.GPIO as GPIO
import time

# Define GPIO pins for different parking status LEDs
LED_PINS = {
    'full': 17,         # Red LED for all spots filled
    'ten_or_less': 27,  # Yellow LED for 10 or fewer spots available
    'more_than_ten': 22  # Green LED for more than 10 spots available
}

# Function to setup GPIO pins
def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Set initial state to LOW (off)

# Function to energize LEDs based on car count
def energize_leds(car_count):
    # Turn off all LEDs first
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    
    # Energize the corresponding LED based on the car count
    if car_count == 0:  # All spots filled
        GPIO.output(LED_PINS['full'], GPIO.HIGH)
        print("All spots filled - Red LED ON")
    elif car_count <= 10:  # 10 or fewer spots available
        GPIO.output(LED_PINS['ten_or_less'], GPIO.HIGH)
        print("10 or fewer spots available - Yellow LED ON")
    else:  # More than 10 spots available
        GPIO.output(LED_PINS['more_than_ten'], GPIO.HIGH)
        print("More than 10 spots available - Green LED ON")

if __name__ == "__main__":
    try:
        setup_gpio()
        
        # Test different scenarios
        test_counts = [0, 5, 15]  # Different car count scenarios
        
        for count in test_counts:
            print(f"Testing car count: {count}")
            energize_leds(count)
            time.sleep(3)  # Wait to observe LED status

        print("Test complete. Cleaning up GPIO.")
    
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    
    finally:
        GPIO.cleanup()  # Ensure GPIO cleanup on exit
