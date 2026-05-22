<div align="center">

# 🤟 Sign Language Detection

### Real-Time ASL Recognition Powered by Computer Vision & Machine Learning

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-0097A7?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7.0-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

> A browser-based application that detects **American Sign Language (ASL)** letters and digits in real time using your webcam — no special hardware required.

<br/>

[🚀 Quick Start](#-quick-start) · [📐 Architecture](#-architecture) · [🔄 Pipeline](#-ml-pipeline) · [🗂️ Project Structure](#️-project-structure) · [🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [ML Pipeline](#-ml-pipeline)
- [Project Structure](#️-project-structure)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [How It Works](#-how-it-works)
- [Supported Signs](#-supported-signs)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🎯 About the Project

Sign Language Detection is a full-stack, end-to-end machine learning web application that bridges communication between the deaf/hard-of-hearing community and the hearing world. Using **Google's MediaPipe** for precise hand landmark extraction and a **Random Forest Classifier** for prediction, the system identifies ASL hand signs in real time directly from your browser — no plugins, no downloads, just your webcam.

The application captures frames from the browser via JavaScript, sends them to a Flask backend, processes hand landmark coordinates using MediaPipe, and returns predictions with a confidence score — all within milliseconds.

---

## ✨ Key Features

- 🎥 **Live Webcam Detection** — Real-time sign recognition via browser without any latency-heavy setup
- 🧠 **ML-Powered Predictions** — Random Forest Classifier trained on normalized MediaPipe hand landmarks
- 🔢 **Full ASL Coverage** — Recognizes all 26 letters (A–Z) and digits (0–9)
- 📊 **Confidence Scoring** — Each prediction is displayed with a confidence percentage
- 🪞 **Mirror Correction** — Automatic horizontal flip for natural, selfie-style interaction
- 🔒 **Thread-Safe Inference** — Uses a threading lock to safely handle concurrent requests to MediaPipe
- 🌐 **Web-Based UI** — Clean browser interface built with HTML, CSS, and JavaScript — no frontend framework needed
- 🔄 **Modular Pipeline** — Data collection, dataset creation, training, and inference are fully separated scripts

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Flask | REST API server, routing, JSON responses |
| **Computer Vision** | OpenCV 4.7.0 | Image decoding, color space conversion, frame flipping |
| **Hand Tracking** | MediaPipe 0.10.9 | 21-point hand landmark extraction |
| **ML Model** | scikit-learn 1.4.2 | Random Forest Classifier training & inference |
| **Numerical** | NumPy 1.26.4 | Feature array construction and normalization |
| **Frontend** | HTML / CSS / JavaScript | Webcam capture, base64 encoding, UI rendering |
| **Serialization** | Pickle | Model and dataset persistence |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BROWSER (Client)                            │
│                                                                     │
│   📷 Webcam  ──►  Canvas (capture frame)  ──►  Base64 Encode       │
│                                                        │            │
│               ◄── Display Prediction + Confidence ◄───┘            │
│                       (JSON Response)                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  POST /predict  (Base64 image)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FLASK SERVER (app.py)                        │
│                                                                     │
│   Decode Base64 ──► OpenCV Decode ──► Flip Frame ──► BGR→RGB       │
│                                                        │            │
│                                                        ▼            │
│                                              MediaPipe Hands        │
│                                           (21 Landmark Points)      │
│                                                        │            │
│                                        Normalize (x - min_x,       │
│                                                   y - min_y)        │
│                                                        │            │
│                                                        ▼            │
│                                         Random Forest Classifier    │
│                                    (42-feature input vector)        │
│                                                        │            │
│                                       Prediction + Confidence       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 ML Pipeline

The project follows a clean four-stage machine learning pipeline:

```
Stage 1          Stage 2           Stage 3          Stage 4
────────         ─────────         ─────────         ──────────
collect_         create_           train_            app.py
images.py   ──►  dataset.py   ──►  model.py    ──►  (Inference)
                                                     
Capture ASL      MediaPipe         Random            Real-time
images per       extracts          Forest            Flask API
class via        landmarks,        trained,          prediction
webcam           pickled to        saved to          via browser
                 data.pickle       model.p           webcam
```

### Stage Details

**Stage 1 — Image Collection (`collect_images.py`)**
Captures raw webcam images for each ASL class (letters A–Z and digits 0–9) and saves them into per-class subdirectories.

**Stage 2 — Dataset Creation (`create_dataset.py`)**
Processes each image through MediaPipe Hands to extract 21 hand landmarks. Coordinates are normalized relative to the hand's bounding box minimum to make the model position-invariant. All feature vectors and labels are serialized to `data.pickle`.

**Stage 3 — Model Training (`train_model.py`)**
Loads `data.pickle`, filters samples to a consistent feature length (42 values = 21 landmarks × 2 axes), splits data 80/20 for training and testing, trains a `RandomForestClassifier`, prints accuracy, and saves the trained model to `model.p`.

**Stage 4 — Inference (`app.py`)**
A Flask server exposes a `/predict` POST endpoint. Each request decodes a base64 webcam frame, processes it through the same MediaPipe landmark pipeline, and queries the trained Random Forest for a prediction and probability score.

---

## 🗂️ Project Structure

```
Sign-Language-Detection/
│
├── app.py                  # 🚀 Flask web server & /predict endpoint
├── collect_images.py       # 📷 Webcam image collection per ASL class
├── create_dataset.py       # 🔬 MediaPipe landmark extraction & pickling
├── train_model.py          # 🧠 Random Forest training & model export
│
├── data.pickle             # 📦 Serialized feature vectors & labels
├── model.p                 # 🤖 Trained Random Forest model
│
├── templates/
│   └── index.html          # 🌐 Frontend — webcam UI & prediction display
│
├── static/
│   ├── style.css           # 🎨 Application styles
│   └── script.js           # ⚙️ Webcam capture & API communication
│
├── requirements.txt        # 📋 Python dependencies
├── .gitignore              # 🚫 Ignored files (venv, __pycache__, etc.)
├── venv_documentation.txt  # 📝 Virtual environment setup notes
└── LICENSE                 # ⚖️ MIT License
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.8 or higher**
- A working **webcam**
- `pip` package manager

### 1. Clone the Repository

```bash
git clone https://github.com/insights-by-sandip/Sign-Language-Detection.git
cd Sign-Language-Detection
```

### 2. Create & Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`. Open that URL in your browser, allow webcam access, and start signing!

---

## 📖 Usage Guide

### Option A — Use the Pre-Trained Model (Recommended for Quick Demo)

The repository already includes `model.p` (trained model) and `data.pickle` (feature dataset). Simply run `app.py` and the app is ready to use immediately.

### Option B — Train Your Own Model from Scratch

Follow the full pipeline to collect your own data and retrain:

**Step 1 — Collect Images**
```bash
python collect_images.py
```
This opens your webcam and captures images for each ASL class. Follow the on-screen prompts to cycle through each sign.

**Step 2 — Build the Dataset**
```bash
python create_dataset.py
```
MediaPipe processes every collected image, extracts hand landmarks, and serializes the feature data to `data.pickle`.

**Step 3 — Train the Model**
```bash
python train_model.py
```
Trains the Random Forest Classifier and reports test accuracy. The trained model is saved to `model.p`.

**Step 4 — Launch the App**
```bash
python app.py
```

---

## ⚙️ How It Works

### Hand Landmark Extraction

MediaPipe Hands detects **21 key points** on the hand (fingertips, knuckles, wrist, etc.). For each landmark, both the `x` and `y` coordinates are captured, producing a raw 42-value vector per hand.

### Position Normalization

To make predictions robust to hand position anywhere in the frame, each coordinate is normalized by subtracting the minimum `x` and `y` values of the detected hand. This makes the feature vector represent hand *shape* rather than hand *position*.

```
normalized_x = landmark.x - min(all_x)
normalized_y = landmark.y - min(all_y)
```

### Random Forest Classification

The 42-element normalized vector is passed to a `RandomForestClassifier` (scikit-learn). The model outputs the predicted class label and, via `predict_proba`, a confidence score ranging from 0–100%.

### Thread Safety

MediaPipe's `Hands` object is not inherently thread-safe. A `threading.Lock` (`mp_lock`) ensures only one HTTP request can access the MediaPipe inference object at a time, preventing crashes under concurrent load.

---

## 🤟 Supported Signs

The model recognizes the following American Sign Language (ASL) signs:

| Category | Signs |
|---|---|
| **Letters** | A B C D E F G H I J K L M N O P Q R S T U V W X Y Z |
| **Digits** | 0 1 2 3 4 5 6 7 8 9 |

> **Total: 36 classes** (26 letters + 10 digits)

---

## 🔧 Configuration

Key parameters you can adjust in `app.py`:

| Parameter | Default | Description |
|---|---|---|
| `min_detection_confidence` | `0.3` | MediaPipe detection threshold (0.0–1.0). Increase for stricter detection. |
| `static_image_mode` | `True` | Set to `False` for video stream mode (faster but less accurate per frame). |
| `model_path` | `./model.p` | Path to the serialized trained model file. |
| `debug` | `True` | Flask debug mode. Set to `False` for production. |

---

## 🩺 Troubleshooting

**Model not loading**
Ensure `model.p` exists in the project root. If missing, run `train_model.py` to regenerate it.

**"No Hand Detected" even with hand visible**
Try improving lighting conditions, move your hand closer to the camera, or lower `min_detection_confidence` to `0.1` in `app.py`.

**Webcam not accessible in browser**
Most browsers require a secure context (HTTPS or localhost) for webcam access. Ensure you're accessing `http://127.0.0.1:5000` (not a network IP) or configure Flask with SSL.

**Slow predictions / high latency**
The threading lock serializes requests. For high-concurrency scenarios, consider running multiple Flask workers with a production WSGI server (e.g., Gunicorn) and instantiating a separate `Hands` object per worker.

**Dependency conflicts**
Use a dedicated virtual environment (see [Quick Start](#-quick-start)) and install exact versions from `requirements.txt` to avoid version mismatch issues.

---

## 🗺️ Roadmap

- [ ] Add support for ASL two-handed signs
- [ ] Word/sentence construction from consecutive letter predictions
- [ ] Text-to-Speech output for detected signs
- [ ] Mobile-responsive UI improvements
- [ ] Dockerize the application for one-command deployment
- [ ] Switch to a deep learning model (CNN/LSTM) for higher accuracy
- [ ] Support for additional sign languages (ISL, BSL, etc.)
- [ ] Real-time FPS counter and performance metrics in the UI

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here's how to get involved:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m 'Add: your feature description'`
4. **Push** to the branch: `git push origin feature/your-feature-name`
5. **Open a Pull Request** with a clear description of what you changed and why

Please make sure your code follows existing style conventions and that any new pipeline steps are documented.

---

## ⚖️ License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sandip Kundu**

[![GitHub](https://img.shields.io/badge/GitHub-insights--by--sandip-181717?style=for-the-badge&logo=github)](https://github.com/insights-by-sandip)

---

<div align="center">

**If you found this project useful, please consider giving it a ⭐ — it means a lot!**

Made with ❤️ and a lot of hand gestures 🤟

</div>
