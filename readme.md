# Automated License Plate Recognition (ALPR) System with Raspberry Pi and Google Cloud

This project implements an automated license plate recognition (ALPR) system using a Raspberry Pi, a camera, an ultrasonic sensor, and Google Cloud Platform's Vision API. The system captures images of vehicles, detects and recognizes license plates, logs the data, and can trigger actions based on the recognized license plate numbers.

## System Architecture

The system consists of the following components:

1. **Raspberry Pi:** Acts as the central processing unit, running the ALPR application.
2. **Camera:** Captures images of vehicles.
3. **Ultrasonic Sensor:** Detects the presence of a vehicle.
4. **Servo Motor:** Controls the position of a gate or barrier (optional).
5. **Google Cloud Platform:**
   - **Cloud Storage:** Stores captured images.
   - **Vision API:** Performs Optical Character Recognition (OCR) to extract text from images.

## Workflow

1. **Vehicle Detection:** The ultrasonic sensor continuously monitors for the presence of a vehicle. When a vehicle is detected, it triggers the image capture process.
2. **Image Capture:** The camera captures an image of the vehicle.
3. **Image Upload:** The captured image is uploaded to a Google Cloud Storage bucket.
4. **License Plate Detection:** Image processing techniques are used to detect the region of the image containing the license plate.
5. **OCR with Google Cloud Vision API:** The Vision API is called to perform OCR on the detected license plate region, extracting the license plate number.
6. **Text Processing and Cleaning:** The extracted text is processed to remove any unnecessary characters and formatted to a standard license plate format.
7. **Data Logging:** The recognized license plate number, along with a timestamp, is logged into a CSV file. The entire OCR result is also logged to a separate text file.
8. **Comparison with Previous Data:** The system can compare the recognized license plate number with previous entries in the CSV file to identify vehicles that have been parked for a certain period.
9. **Action Trigger:** Based on the recognized license plate number and other logic, the system can trigger actions such as:
   - Opening or closing a gate.
   - Sending notifications.
   - Logging entry and exit times.

## Project Files

- **`car.py`:** Contains code for the ultrasonic sensor and basic car detection logic. It also includes a simple web server to send car presence status to a webpage.
- **`ocr_script.py`:** Contains the core ALPR logic, including image capture, upload to Google Cloud, license plate detection, OCR, text processing, and data logging.
- **`runner.py`:** Combines the functionality of `car.py` and `ocr_script.py`. It triggers the OCR script when a car is detected and controls a servo motor based on the recognized license plate.
- **`test.py`:** An alternative version that integrates all the components into a single script for testing and development.
- **`index.html`:** A basic HTML webpage to display captured images, OCR results, and CSV data.
- **`style.css`:** Contains the CSS styles for the webpage.
- **`script.js`:** Contains JavaScript code for interacting with the webpage and displaying data.

## Prerequisites

- Raspberry Pi with a compatible camera and ultrasonic sensor.
- Raspberry Pi OS installed and configured.
- Python 3 and necessary libraries installed: OpenCV, Google Cloud Storage, Google Cloud Vision.
- Google Cloud Platform account with billing enabled.
- Google Cloud Storage bucket created.
- Service account key file (JSON) for accessing Google Cloud APIs.

## Installation and Setup

1. Clone the repository to your Raspberry Pi.
2. Install the required Python libraries.
3. Configure the Google Cloud Platform settings in the `ocr_script.py` file, including the bucket name and service account key file path.
4. Connect the camera and ultrasonic sensor to the Raspberry Pi.
5. Update the GPIO pin configurations in the Python scripts to match your hardware setup.

## Running the Application

- To run the application, execute the `test.py` script using Python 3.
- Open the `index.html` file in a web browser to view the dashboard.

## Future Enhancements

- Implement more robust license plate detection algorithms to improve accuracy in challenging conditions.
- Integrate with a database to store and manage license plate data more efficiently.
- Develop a user interface for configuring system settings and viewing data.
- Add support for different types of cameras and sensors.

## Disclaimer

This project is for educational and demonstration purposes only. It is not intended for production use in real-world traffic monitoring or law enforcement applications.

---