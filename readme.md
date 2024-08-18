# Automated License Plate Recognition (ALPR) System with Raspberry Pi, Google Cloud, and Node.js Dashboard

This project implements an automated license plate recognition (ALPR) system using a Raspberry Pi, camera, ultrasonic sensor, and leverages Google Cloud Platform's Vision API. The recognized data is visualized through a dynamic web dashboard powered by Node.js.

## System Architecture

The system is comprised of the following components:

1. **Raspberry Pi:** Serves as the primary processing unit, running the ALPR application and interfacing with hardware components.
2. **Camera:** Captures images of vehicles.
3. **IR Sensor:** Detects the presence of a vehicle, triggering the image capture process.
4. **Servo Motor:** Controls a gate or barrier based on license plate recognition results (optional).
5. **Google Cloud Platform:**
    - **Cloud Storage:** Provides storage for captured images.
    - **Vision API:** Executes Optical Character Recognition (OCR) to extract text from images.
6. **Node.js Web Server:** Hosts the dynamic web dashboard, providing real-time updates on captured images, OCR results, and system status.

## Workflow

1. **Vehicle Detection:** The ultrasonic sensor continuously monitors for a vehicle's presence. Upon detection, it signals the Raspberry Pi to capture an image.
2. **Image Capture:** The camera, triggered by the Raspberry Pi, captures an image of the vehicle.
3. **Image Upload:** The captured image is transmitted to a designated Google Cloud Storage bucket.
4. **License Plate Detection:** Advanced image processing algorithms pinpoint the region within the image containing the license plate.
5. **OCR with Google Cloud Vision API:** The isolated license plate region is sent to the Vision API for OCR, extracting the license plate number.
6. **Text Processing and Cleaning:** Extracted text undergoes processing to eliminate extraneous characters and conform to standard license plate formatting.
7. **Data Logging:** The recognized license plate number, accompanied by a timestamp, is logged to a CSV file. Additionally, the comprehensive OCR result is saved to a dedicated text file.
8. **Data Synchronization with Node.js Server:** The Raspberry Pi communicates the processed data (license plate number, timestamp, any additional relevant information) to the Node.js server.
9. **Real-time Dashboard Updates:** The Node.js server, upon receiving data from the Raspberry Pi, updates the web dashboard in real-time. This includes displaying captured images, recognized license plate numbers, timestamps, and potentially other system metrics.
10. **Action Trigger & Control (Optional):** The system can be configured to trigger actions based on the recognized license plate number. For instance, if a match is found against a database of authorized vehicles, a signal can be sent to open a gate. The Node.js server can facilitate the control interface for such actions. 

## Project Files

- **`test.py`:** Contains the consolidated ALPR logic, encompassing vehicle detection, image capture, processing, OCR, data logging, and communication with the Node.js server.
- **`server.js`:** Houses the Node.js server code responsible for handling API requests from the dashboard, receiving data from `test.py`, and serving the frontend files.
- **`index.html`:** The main HTML file for the web dashboard, providing the structure and layout for displaying ALPR data.
- **`style.css`:** Contains the CSS styles for customizing the appearance of the web dashboard.
- **`script.js`:** Includes JavaScript code for handling user interactions within the dashboard, fetching data from the Node.js server, and dynamically updating the content.

## Getting Started

1. **Raspberry Pi Setup:**
   - Install Raspberry Pi OS and ensure it has internet connectivity.
   - Connect the camera, ultrasonic sensor, and servo motor (if applicable).
   - Install necessary Python libraries: OpenCV, Google Cloud Storage, Google Cloud Vision.
2. **Google Cloud Platform Configuration:**
   - Create a Google Cloud Project and enable billing.
   - Set up a Google Cloud Storage bucket to store images.
   - Generate a service account key file (JSON) for API access and securely store it on the Raspberry Pi.
3. **Node.js Server Installation:**
   - Install Node.js and npm on your Raspberry Pi or a system that will host the server.
   - Navigate to the project directory and install project dependencies: `npm install`.
4. **Configuration:**
   - Update `test.py` with:
     - Correct GPIO pin configurations for your hardware.
     - Google Cloud Storage bucket name.
     - Path to your Google Cloud service account key file.
     - Node.js server address and port if not running on the same device.
   - Update `server.js` to listen on the desired port and adjust any file paths if necessary.
5. **Running the System:**
   - Start the Node.js server: `node server.js`.
   - Execute the Python script: `python3 test.py`.

Now, access the dashboard through a web browser by navigating to the server's IP address and port (e.g., `http://[Raspberry Pi IP Address]:[Port]`). 

## Future Enhancements

- **Database Integration:** Store license plate data, timestamps, and other relevant information in a database for persistent storage, retrieval, and more sophisticated analysis.
- **Enhanced User Interface:** Design a more interactive and user-friendly web dashboard with features for data visualization, historical analysis, user management, and system control.
- **Advanced Analytics:** Implement image processing techniques for license plate type identification, vehicle color detection, and potentially integration with other computer vision models.
- **Real-time Alerts:** Configure the system to trigger alerts based on specific criteria, such as blacklisted license plates, unauthorized vehicles, or parking time violations. 

**Remember:** This project is intended for educational and proof-of-concept purposes. It is not suitable for production environments involving sensitive information or critical infrastructure without proper security measures and legal considerations. 
