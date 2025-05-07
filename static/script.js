// --- Global Variables ---
let videoStream = null;
let wasWebsiteActive = true;
let uploadedImageData = null; 
let autoCaptureInterval = null;


async function populateWebcamOptions() {
    const webcamSelect = document.getElementById('webcamSelect');
    if (!webcamSelect) {
        console.error("❌ Webcam select element not found!");
        return;
    }
    
    console.log("📡 Requesting camera permissions...");

    try {
        // ✅ Request Camera Permissions
        await navigator.mediaDevices.getUserMedia({ video: true });

        // ✅ Get Available Devices
        const devices = await navigator.mediaDevices.enumerateDevices();
        console.log("📡 Devices found:", devices);

        webcamSelect.innerHTML = ''; // Clear previous options

        // ✅ Filter only video devices
        const videoDevices = devices.filter(device => device.kind === "videoinput");

        if (videoDevices.length === 0) {
            const option = document.createElement("option");
            option.text = "No webcam found";
            option.disabled = true;
            webcamSelect.appendChild(option);
        } else {
            videoDevices.forEach((device, index) => {
                const option = document.createElement("option");
                option.value = device.deviceId;
                option.text = device.label || `Camera ${index + 1}`;
                webcamSelect.appendChild(option);
            });

            // ✅ Ensure the first available camera is selected
            webcamSelect.selectedIndex = 0;
        }
    } catch (err) {
        console.error("❌ Webcam error:", err);
        alert("Error accessing webcam. Please grant permission and reload.");
    }
}

window.addEventListener("load", async function () {
    console.log("🚀 Checking backend status...");
    await new Promise(resolve => setTimeout(resolve, 2000));  // Wait 2 seconds
    const isBackendAvailable = await checkBackendStatus();
    if (!isBackendAvailable) {
        alert("Backend is not running! Start the backend before using the app.");
    }
    await populateWebcamOptions();
});



// --- Start/Stop Camera ---
async function startCamera() {
    stopCamera();
    const webcamSelect = document.getElementById('webcamSelect');
    const selectedCameraId = webcamSelect.value;
    
    if (!selectedCameraId) {
        alert("No camera selected! Please choose a device.");
        return;
    }

    const video = document.getElementById('webcam');
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: selectedCameraId } }
        });

        video.srcObject = videoStream;
        video.style.display = "block";
    } catch (err) {
        console.error("❌ Camera error:", err);
        alert("Error accessing camera: " + err.message);
    }
}



function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

function startAutomaticCapture() {
    clearInterval(autoCaptureInterval); // Ensure no duplicate intervals
    autoCaptureInterval = setInterval(() => {
        captureImage();
    }, 5000); // Capture every 1 minute (60000 ms)
}

// --- Stop Automatic Capture ---
function stopAutomaticCapture() {
    clearInterval(autoCaptureInterval);
}

// --- Manual Capture Mode ---
function enableManualCapture() {
    stopAutomaticCapture();
}

// --- Event Listeners for Capture Modes ---
document.getElementById("autoCaptureBtn").addEventListener("click", startAutomaticCapture);
document.getElementById("manualCaptureBtn").addEventListener("click", enableManualCapture);


function previewImage(event) {
    var preview = document.getElementById("preview");
    var file = event.target.files[0];

    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
        };
        reader.readAsDataURL(file);
    }
}
// --- Process Image on Button Click ---
document.getElementById("processImageBtn").addEventListener("click", () => {
    if (uploadedImageData) {
        
        processImage(uploadedImageData);
    } else {
        alert("Please upload an image first.");
    }
});

async function checkBackendStatus() {
    let attempts = 0;
    let backendReady = false;

    while (attempts < 5) { // Try up to 5 times before giving up
        try {
            console.log(`🚀 Checking backend status... Attempt ${attempts + 1}`);
            const response = await fetch("http://127.0.0.1:8000/healthcheck", { method: "GET" });

            if (response.ok) {
                console.log("✅ Backend is online!");
                backendReady = true;
                break;
            }
        } catch (err) {
            console.warn(`⚠️ Backend not ready yet... Retrying in 2 seconds (${attempts + 1}/5)`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        attempts++;
    }

    if (!backendReady) {
        console.error("❌ Backend failed to start after multiple attempts!");
        alert("Backend is not available. Please start the server.");
    }

    return backendReady;
}

async function processImage(imageData) {
    const shift = document.getElementById("shiftSelect").value;

    if (!imageData || !shift) {
        alert("Please upload an image or capture one, and select a shift.");
        return;
    }

    let backendReady = await checkBackendStatus();
    if (!backendReady) return;

    let attempts = 0;
    let maxAttempts = 3;

    while (attempts < maxAttempts) {
        try {
            console.log(`📤 Sending image to backend... Attempt ${attempts + 1}`);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 sec timeout

            const response = await fetch("http://127.0.0.1:8000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                mode: "cors",
                body: JSON.stringify({ image: imageData, shift: shift }),
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                console.error("❌ Backend error:", await response.text());
                alert("Error from server.");
                return;
            }

            const data = await response.json();
            console.log("✅ Processed data:", data);

            // Update UI
            document.getElementById("brand").textContent = data.brand || "---";
            document.getElementById("color").textContent = data.color || "---";
            document.getElementById("flavor").textContent = data.flavor || "---";
            document.getElementById("ingredients").textContent = data.ingredients || "---";
            document.getElementById("detection_status").textContent = data.detection_status || "---";

            return;
        } catch (err) {
            console.error("❌ Fetch error:", err);
            attempts++;

            if (attempts >= maxAttempts) {
                alert("Failed to connect to backend after multiple attempts. Check console.");
                return;
            }

            console.warn(`⚠️ Retrying in 3 seconds (${attempts}/${maxAttempts})...`);
            await new Promise(resolve => setTimeout(resolve, 3000));
        }
    }
}



function captureImage() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const previewImage = document.getElementById('previewImage');

    if (!videoStream) {
        console.error("❌ Webcam not active!");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    let imageDataURL = canvas.toDataURL('image/png');

    // ✅ Check if imageDataURL is valid
    if (!imageDataURL) {
        console.error("❌ Image data is missing!");
        alert("Image capture failed. Please try again.");
        return;
    }

    // ✅ Display the captured image
    previewImage.src = imageDataURL;
    previewImage.style.display = "block";

    // ✅ Resize and process image
    resizeImage(imageDataURL, 800, 600, (resizedDataURL) => {
        processImage(resizedDataURL);
    });
}

function resizeImage(imageDataURL, maxWidth, maxHeight, callback) {
    if (!imageDataURL) {
        console.error("❌ No image data provided for resizing!");
        return;
    }

    const img = new Image();
    img.src = imageDataURL;
    
    img.onload = function() {
        let canvas = document.createElement("canvas");
        let ctx = canvas.getContext("2d");
        
        let width = img.width;
        let height = img.height;

        if (width > height) {
            if (width > maxWidth) {
                height = Math.round((height * maxWidth) / width);
                width = maxWidth;
            }
        } else {
            if (height > maxHeight) {
                width = Math.round((width * maxHeight) / height);
                height = maxHeight;
            }
        }

        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);

        const resizedImageDataURL = canvas.toDataURL("image/png");
        callback(resizedImageDataURL);
    };
}

// --- Shift Configuration ---
const shifts = {
    shift1: { start: 6, end: 14, break: [10, 10.5], lunch: [12, 12.5] },
    shift2: { start: 14, end: 22, break: [18, 18.5], lunch: [20, 20.5] },
    shift3: { start: 22, end: 30, break: [26, 26.5], lunch: [28, 28.5] }
};


window.addEventListener("blur", () => {
    if (wasWebsiteActive) {
        wasWebsiteActive = false;    
    }
});


window.addEventListener("focus", () => {
    if (!wasWebsiteActive) {
        wasWebsiteActive = true;
    }
});

function openDashboard() {
    fetch('/open_dashboard')
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                console.log("Dashboard started. Open it manually if needed: " + data.url);
            } else {
                alert("Failed to open dashboard: " + data.error);
            }
        })
        .catch(() => {
            alert("Failed to open dashboard");
        });
}

document.addEventListener("DOMContentLoaded", function () {
    // 📊 Dashboard Button
    const openDashboardBtn = document.getElementById("openDashboardBtn");
    if (openDashboardBtn) {
        openDashboardBtn.addEventListener("click", openDashboard);
    }

    // 📸 Image Upload Handling
    const imageUploadInput = document.getElementById("imageUpload");
    if (imageUploadInput) {
        imageUploadInput.addEventListener("change", async function(event) {
            const file = event.target.files[0];

            if (file) {
                try {
                    console.log("📉 Compressing image before processing...");
                    const compressedImage = await imageCompression(file, { maxSizeMB: 1 });

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        uploadedImageData = e.target.result;  // Base64 image data
                        console.log("📸 Compressed image ready for processing.");

                        // Optional: show preview
                        const preview = document.getElementById("preview");
                        if (preview) {
                            preview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image" style="max-width: 100%; border-radius: 8px;">`;
                        }
                    };
                    reader.readAsDataURL(compressedImage);
                } catch (err) {
                    console.error("❌ Image compression error:", err);
                    alert("Failed to compress image.");
                }
            }
        });
    }
});