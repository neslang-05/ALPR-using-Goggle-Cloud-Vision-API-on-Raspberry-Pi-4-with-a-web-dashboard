import RPi.GPIO as GPIO
import time
import threading
import socket
import json

# GPIO Pin Configuration
TRIG_PIN = 23
ECHO_PIN = 24

# Server Settings
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Distance threshold for car detection (in cm)
DISTANCE_THRESHOLD = 1

# Flag for car presence
car_present = False

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Function to measure distance using ultrasonic sensor
def measure_distance():
    global car_present
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    if distance < DISTANCE_THRESHOLD:
        car_present = True
    else:
        car_present = False

    return distance

# Function to run the ultrasonic sensor in a separate thread
def ultrasonic_sensor_thread():
    while True:
        distance = measure_distance()
        time.sleep(0.1)  # Adjust the delay as needed

# Function to create and run the server
def start_server():
    global car_present
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024).decode('utf-8')
                if data:
                    # Send car presence status to the webpage
                    response = {"car_present": car_present}
                    conn.sendall(json.dumps(response).encode('utf-8'))
                else:
                    break

# Start the ultrasonic sensor thread
ultrasonic_thread = threading.Thread(target=ultrasonic_sensor_thread)
ultrasonic_thread.daemon = True
ultrasonic_thread.start()

# Start the server
start_server()

# Cleanup GPIO
GPIO.cleanup()