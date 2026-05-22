// --- DOM Elements ---
const video = document.getElementById("videoElement");
const canvas = document.getElementById("canvas");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const overlay = document.getElementById("cameraOverlay");
const predictionEl = document.getElementById("currentPrediction");
const statusText = document.getElementById("statusText");
const voiceToggle = document.getElementById("voiceToggle");
const confidenceBar = document.getElementById("confidenceBar");
const confidenceText = document.getElementById("confidenceText");
const cameraSelect = document.getElementById("cameraSelect");

// Modal Elements
const helpBtn = document.getElementById("helpBtn");
const helpModal = document.getElementById("helpModal");
const closeModalSpan = document.getElementsByClassName("close-modal")[0];

// --- Variables ---
let isProcessing = false;
let stream = null;
let lastPrediction = "";

// --- Main Event Listeners ---
startBtn.addEventListener("click", () => {
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            video.srcObject = stream;
            
            // UI State: ON
            overlay.style.display = "none";
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusText.innerText = "ONLINE";
            statusText.style.color = "#00f3ff";
            
            isProcessing = true;
            processFrame();
        })
        .catch(err => {
            console.error(err);
            alert("Camera Access Denied or Not Found");
        });
    }
});

stopBtn.addEventListener("click", () => {
    isProcessing = false;
    if (stream) stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;

    // UI State: OFF
    overlay.style.display = "flex";
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusText.innerText = "STANDBY";
    statusText.style.color = "#64748b";
    
    // Reset Data
    predictionEl.innerText = "--";
    predictionEl.classList.remove("active");
    confidenceBar.style.width = "0%";
    confidenceText.innerText = "0%";

    window.speechSynthesis.cancel();
});

// --- Modal Event Listeners ---
helpBtn.onclick = function() {
    helpModal.style.display = "block";
}

closeModalSpan.onclick = function() {
    helpModal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == helpModal) {
        helpModal.style.display = "none";
    }
}

// --- Processing Loop ---
function processFrame() {
    if (!isProcessing) return;

    const ctx = canvas.getContext('2d');
    // Draw small frame for performance
    ctx.drawImage(video, 0, 0, 320, 240);
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL })
    })
    .then(res => res.json())
    .then(data => {
        updateUI(data.prediction, data.confidence);
        if (isProcessing) requestAnimationFrame(processFrame);
    })
    .catch(err => {
        // If error, retry after 1s
        if (isProcessing) setTimeout(processFrame, 1000);
    });
}

// --- UI Updates ---
function updateUI(pred, conf) {
    if (pred === "No Hand Detected" || pred === "Unknown" || pred === "Error") {
        predictionEl.innerText = "--";
        predictionEl.classList.remove("active");
        confidenceBar.style.width = "0%";
        confidenceText.innerText = "0%";
        return;
    }

    // Update Text
    predictionEl.innerText = pred;
    predictionEl.classList.add("active");

    // Update Bar
    // Default to visual 85% if model doesn't support probability
    let displayConf = conf > 0 ? conf : 85; 
    confidenceBar.style.width = `${displayConf}%`;
    confidenceText.innerText = `${Math.round(displayConf)}%`;

    // Voice Logic
    if (pred !== lastPrediction) {
        lastPrediction = pred;
        if (voiceToggle.checked) {
            window.speechSynthesis.cancel();
            let msg = new SpeechSynthesisUtterance(pred);
            msg.rate = 1.2;
            window.speechSynthesis.speak(msg);
        }
    }
}



// --- 1. Get Camera List on Load ---
async function getCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        cameraSelect.innerHTML = ""; // Clear list
        
        videoDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${index + 1}`;
            cameraSelect.appendChild(option);
        });

        if (videoDevices.length === 0) {
            const option = document.createElement('option');
            option.text = "No cameras found";
            cameraSelect.appendChild(option);
        }
    } catch (err) {
        console.error("Error fetching cameras:", err);
    }
}

// Call this immediately to populate the dropdown
getCameras();

// --- 2. Handle Camera Change ---
cameraSelect.addEventListener('change', () => {
    // If the camera is currently running, stop it and restart with the new one
    if (isProcessing) {
        stopCameraLogic(); // Helper function (see below)
        startCameraLogic(); // Helper function (see below)
    }
});


// --- 3. Updated Start/Stop Functions ---

// We split the logic so we can reuse it for switching
startBtn.addEventListener("click", startCameraLogic);
stopBtn.addEventListener("click", stopCameraLogic);

function startCameraLogic() {
    const selectedCameraId = cameraSelect.value;
    
    // Constraints: Ask for the specific device ID
    const constraints = {
        video: {
            deviceId: selectedCameraId ? { exact: selectedCameraId } : undefined,
            width: { ideal: 640 }, // Optional: Ask for specific resolution
            height: { ideal: 480 }
        }
    };

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then(s => {
            stream = s;
            video.srcObject = stream;
            
            // UI Updates
            overlay.style.display = "none";
            startBtn.disabled = true;
            stopBtn.disabled = false;
            cameraSelect.disabled = true; // Lock selection while starting
            statusText.innerText = "ONLINE";
            statusText.style.color = "#00f3ff";
            
            // Re-enable selection after a moment so user can switch live
            setTimeout(() => { cameraSelect.disabled = false; }, 1000);

            isProcessing = true;
            processFrame();
        })
        .catch(err => {
            console.error(err);
            alert("Error accessing camera. Ensure permissions are granted.");
        });
    }
}

function stopCameraLogic() {
    isProcessing = false;
    if (stream) stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;

    // UI Updates
    overlay.style.display = "flex";
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusText.innerText = "STANDBY";
    statusText.style.color = "#64748b";
    
    predictionEl.innerText = "--";
    predictionEl.classList.remove("active");
    confidenceBar.style.width = "0%";
    confidenceText.innerText = "0%";
    
    window.speechSynthesis.cancel();
}