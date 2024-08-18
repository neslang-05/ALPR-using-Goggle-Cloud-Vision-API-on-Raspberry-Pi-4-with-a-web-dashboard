import time
import subprocess
import RPi.GPIO as GPIO

# GPIO pin configuration
IR_SENSOR_PIN = 17  # GPIO pin for the IR sensor
SERVO_PIN = 16      # GPIO pin for the servo motor

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo motor setup
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
pwm.start(0)  # Initial duty cycle of 0%

def run_ocr_script():
    """Runs the OCR script."""
    try:
        subprocess.run(['python3', 'ocr_script.py'], check=True)
        print("OCR script completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running OCR script: {e}")

def move_servo_to_90_degrees():
    """Moves the servo motor to 90 degrees."""
    pwm.ChangeDutyCycle(7.5)  # 7.5% duty cycle corresponds to 90 degrees
    time.sleep(0.2)  # Wait for the servo to reach the position
    pwm.ChangeDutyCycle(0)  # Stop sending PWM signal

def move_servo_to_180_degrees():
    """Moves the servo motor to 180 degrees."""
    pwm.ChangeDutyCycle(12.5)  # 12.5% duty cycle corresponds to 180 degrees
    time.sleep(0.2)  # Wait for the servo to reach the position
    pwm.ChangeDutyCycle(0)  # Stop sending PWM signal

try:
    while True:
        if GPIO.input(IR_SENSOR_PIN):
            # No object detected
            print("No object detected.")
            time.sleep(0.2)  # Wait for 3 seconds before moving the servo
            move_servo_to_180_degrees()
            print("Servo motor moved to 180 degrees.")
        else:
            # Object detected
            print("Object detected.")
            run_ocr_script()
            move_servo_to_90_degrees()
            print("Servo motor moved to 90 degrees.")
        
        time.sleep(1)  # Delay before next check

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO settings
