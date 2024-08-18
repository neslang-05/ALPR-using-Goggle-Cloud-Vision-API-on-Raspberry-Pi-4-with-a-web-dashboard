import cv2
import os
from google.cloud import storage
from google.cloud import vision
import datetime
import re
import csv
import logging
import json
import RPi.GPIO as GPIO
import time
import subprocess

# GPIO pin configuration
IR_SENSOR_PIN = 17  # GPIO pin for the IR sensor
SERVO_PIN = 16      # GPIO pin for the servo motor

# Directory for saving images and CSV file
FILES_DIR = '/home/neslang/Documents/ALPR/files'

# Google Cloud settings
BUCKET_NAME = "raspi-ocr-gcp-bucket"
BLOB_NAME = "captured_image.jpg"
GCS_CREDENTIALS = '/home/neslang/project/secrets.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCS_CREDENTIALS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create files directory if not exists
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# --- Image Capture ---
def capture_and_upload_image():
    """Captures image, uploads to GCS."""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        logging.error("Cannot open webcam")
        raise IOError("Cannot open webcam")

    try:
        ret, frame = camera.read()
        if ret:
            captured_image_path = os.path.join(FILES_DIR, "captured_image.jpg")
            cv2.imwrite(captured_image_path, frame)
            logging.info("Image captured and saved locally.")

            upload_blob(BUCKET_NAME, captured_image_path, BLOB_NAME)
            logging.info(f"Image uploaded to gs://{BUCKET_NAME}/{BLOB_NAME}")
        else:
            logging.error("Error capturing image.")
    finally:
        camera.release()

# --- Google Cloud Storage (GCS) ---
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads file to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

# --- License Plate Detection ---
def detect_license_plate(image_path):
    """Detects license plate region."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(c)
            license_plate = img[y:y + h, x:x + w]
            license_plate_path = os.path.join(FILES_DIR, "license_plate.jpg")
            cv2.imwrite(license_plate_path, license_plate)  # Save the detected license plate image
            return license_plate_path
    logging.info("License plate not detected.")
    return None

# --- Google Cloud Vision API (OCR) ---
def perform_ocr_with_gcp(image_path):
    """Performs OCR using Google Cloud Vision."""
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    try:
        response = client.text_detection(image=image)
        texts = response.text_annotations
    except Exception as e:
        logging.error(f"Error during OCR: {e}")
        return None, None

    ocr_full_text = ''
    license_plate_text = None
    for text in texts:
        ocr_full_text += text.description + ' '
        if len(text.description) >= 6:
            license_plate_text = text.description

    return license_plate_text, ocr_full_text

# --- Text Filtering and Cleaning ---
def filter_license_plate_text(ocr_text):
    """Filters out unnecessary text and cleans the license plate string."""
    if ocr_text is None:
        return None

    ocr_text = ocr_text.replace('\n', ' ')  # Replace newlines with spaces

    # Remove common unwanted words/patterns
    words_to_remove = ["car", "vehicle", "IND", "India",  # Add more as needed
                       r"\b[A-Z]{2}[0-9]{2}\b",  # Remove state codes (e.g., DL12)
                       r"\b[0-9]{2}[A-Z]{2}\b"]  # Remove patterns like 12DL
    for word in words_to_remove:
        ocr_text = re.sub(word, "", ocr_text, flags=re.IGNORECASE)

    # Additional cleaning:
    ocr_text = ocr_text.strip()  # Remove leading/trailing whitespace
    ocr_text = re.sub(' +', ' ', ocr_text)  # Remove extra spaces

    return ocr_text

# --- Error Correction ---
def correct_errors(text):
    """Applies basic OCR error correction."""
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("B", "8")
    return text

# --- CSV Logging ---
def append_to_csv(data, filename=os.path.join(FILES_DIR, "license_plates.csv")):
    """Appends data to CSV with timestamp (single line)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, 'a') as csvfile:
            csvfile.write(f"{timestamp},{data}\n")
    except Exception as e:
        logging.error(f"Error writing to CSV: {e}")

#Function to compare with previous data 
def compare_with_previous_data(data, filename=os.path.join(FILES_DIR, "license_plates.csv")):
    """Compares the last 4-6 characters of the data with previous entries."""
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:  # Check if the row has at least two columns
                    previous_data = row[1]
                    if data[-6:] == previous_data[-6:]:
                        logging.info("License data matched (last 6 characters): %s", data[-6:])
                        time_difference = calculate_time_difference(row[0]) 
                        logging.info("Time parked: %s", time_difference)
                        return True, time_difference
                    elif data[-4:] == previous_data[-4:]:
                        logging.info("License data matched (last 4 characters): %s", data[-4:])
                        time_difference = calculate_time_difference(row[0])
                        logging.info("Time parked: %s", time_difference)
                        return True, time_difference
    except FileNotFoundError:
        logging.info("CSV file not found. Assuming first entry.")
    except Exception as e:
        logging.error(f"Error comparing data: {e}")
    logging.info("License data not found.")
    return False, None  # Return None for time difference if not found

# --- Function to calculate the time differnce ---
def calculate_time_difference(timestamp_str):
    """Calculates the time difference between now and the provided timestamp."""
    try:
        previous_time = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now()
        return str(current_time - previous_time)
    except ValueError:
        logging.error("Invalid timestamp format in CSV file.")
        return None

# --- JSON Logging ---
def log_to_json(data, time_parked, filename=os.path.join(FILES_DIR, "license_plates.json")):
    """Appends data to JSON file with timestamp and time parked."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, 'w') as json_file:  # Open in write mode ('w') to clear previous content
            json.dump({"timestamp": timestamp, "license_plate": data, "time_parked": time_parked}, json_file, indent=4)
    except Exception as e:
        logging.error(f"Error writing to JSON file: {e}")

# --- After detecting and processing license plate ---
def append_to_txt(ocr_result, filename=os.path.join(FILES_DIR, "ocr_result.txt")):
    """Writes the entire OCR result to a text file."""
    try:
        with open(filename, 'w') as file:
            file.write(ocr_result)
    except Exception as e:
        logging.error(f"Error writing to text file: {e}")

# --- Servo Motor Control ---
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

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo motor setup
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
pwm.start(0)  # Initial duty cycle of 0%

# Main execution
if __name__ == "__main__":
    try:
        while True:
            if GPIO.input(IR_SENSOR_PIN):
                # No object detected
                print("No object detected.")
                time.sleep(0.5)  # Wait for 3 seconds before moving the servo
                move_servo_to_180_degrees()
                print("Servo motor moved to 180 degrees.")
            else:
                # Object detected
                print("Object detected.")
                capture_and_upload_image()
                image_path = os.path.join(FILES_DIR, "captured_image.jpg")

                detected_license_plate_image = detect_license_plate(image_path)
                if detected_license_plate_image is not None:
                    logging.info("License detected")
                    license_plate_text, ocr_full_text = perform_ocr_with_gcp(detected_license_plate_image)
                    if license_plate_text:
                        filtered_text = filter_license_plate_text(license_plate_text)
                        corrected_text = correct_errors(filtered_text)
                        logging.info("License Plate: %s", corrected_text)
                        matched, time_parked = compare_with_previous_data(corrected_text)
                        move_servo_to_90_degrees()
                        if matched:
                            logging.info("License data matched. Taking appropriate action...")
                            log_to_json(corrected_text, time_parked)  # Log to JSON with time parked
                            move_servo_to_90_degrees()  # Move servo only if license plate matches
                            print("Servo motor moved to 90 degrees.")
                            run_ocr_script()  # Run OCR script after servo movement
                        else:
                            logging.info("License data not found. Taking appropriate action...")
                            append_to_csv(corrected_text)
                            append_to_txt(ocr_full_text)  # Save the full OCR result
                            log_to_json(corrected_text, None)  # Log to JSON with None for time parked
                            logging.info("License plate data appended to CSV file, OCR result to text file, and JSON file.")
                    else:
                        logging.error("OCR could not extract license plate text.")
                        append_to_txt(ocr_full_text)  # Save the full OCR result even if no license plate detected
                else:
                    logging.info("License plate not detected.")
            
            time.sleep(1)  # Delay before next check

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        pwm.stop()  # Stop PWM
        GPIO.cleanup()  # Clean up GPIO settings