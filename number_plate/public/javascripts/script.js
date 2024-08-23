// Fetch available slots and update the display
function updateSlots() {
    fetch('/slots')
        .then(response => response.json())
        .then(data => {
            document.getElementById('slots').textContent = `Available Slots: ${data.availableSlots} / ${data.totalSlots}`;
        })
        .catch(error => console.error('Error fetching slots:', error));
}

// Fetch OCR results and update the display
function updateOCRResults() {
    fetch('/ocr-results')
        .then(response => response.json())
        .then(data => {
            document.getElementById('license-plate').textContent = data.license_plate || 'N/A';
            document.getElementById('timestamp').textContent = data.timestamp || 'N/A';
            document.getElementById('time-parked').textContent = data.time_parked || 'N/A';
        })
        .catch(error => console.error('Error fetching OCR results:', error));
}

// Fetch CSV data and populate the table
function updateCSVTable() {
    fetch('/csv-data')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#csvTable tbody');
            tbody.innerHTML = '';
            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.licensePlate}</td>
                    <td>${row.timestamp}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error fetching CSV data:', error));
}

// Run OCR when the button is clicked
function runOCR() {
    fetch('/run-ocr', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('OCR Data:', data);
            updateOCRResults();
            updateSlots();
            updateCSVTable();
        })
        .catch(error => console.error('Error running OCR:', error));
}

// Refresh all data
function refreshData() {
    updateOCRResults();
    updateSlots();
    updateCSVTable();
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    updateSlots();
    updateOCRResults();
    updateCSVTable();
    autoRefresh();
});

// Function to refresh images, CSV data, and OCR results every 3 seconds
function autoRefresh() {
    setInterval(() => {
        // Refresh the captured images
        document.getElementById('capturedImage').src = `/captured_image?${new Date().getTime()}`;
        document.getElementById('licensePlateImage').src = `/license_plate?${new Date().getTime()}`;

        // Refresh the CSV table data
        updateCSVTable();

        // Refresh the OCR results
        updateOCRResults();

        // Refresh the available slots
        updateSlots();
    }, 3000); // 3000 milliseconds = 3 seconds

    // Live Stream Logic
    const startStreamButton = document.getElementById('startStream');
    const stopStreamButton = document.getElementById('stopStream');
    const liveStreamFrame = document.getElementById('liveStream');
    const liveStreamUrl = 'http://192.168.29.207:4747/';

    startStreamButton.addEventListener('click', function() {
        liveStreamFrame.src = liveStreamUrl;
        liveStreamFrame.style.display = 'block';
    });

    stopStreamButton.addEventListener('click', function() {
        liveStreamFrame.src = 'http://192.168.29.207:4747/';
        liveStreamFrame.style.display = 'none';
    });
}
