from flask import Flask, render_template, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import pickle
import base64
import os
import threading  # <--- NEW IMPORT

app = Flask(__name__)

# --- 1. CONFIGURATION & LOAD MODEL ---
model_path = './model.p'

if os.path.exists(model_path):
    model_dict = pickle.load(open(model_path, 'rb'))
    model = model_dict['model']
    print("✅ Model loaded successfully!")
else:
    print(f"❌ Error: '{model_path}' not found.")
    model = None

# --- 2. MEDIAPIPE SETUP ---
mp_hands = mp.solutions.hands
# static_image_mode=True is good for independent images, but the object itself 
# cannot be shared across threads without locking.
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Create a Lock to prevent multiple threads from accessing MediaPipe simultaneously
mp_lock = threading.Lock() # <--- NEW LOCK

# Labels Dictionary
labels_dict = {
    0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 
    'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N', 'O': 'O', 'P': 'P', 
    'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'prediction': "Model Error", 'confidence': 0})

    try:
        data = request.json['image']
        
        # 1. Decode Image
        header, encoded = data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2. Flip Image (Mirror Effect)
        frame = cv2.flip(frame, 1)

        # 3. Process with Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # --- CRITICAL FIX START ---
        # We lock this section so only ONE request can use 'hands' at a time.
        with mp_lock:
            results = hands.process(frame_rgb)
        # --- CRITICAL FIX END ---
        
        predicted_character = "No Hand Detected"
        confidence_score = 0.0

        if results.multi_hand_landmarks:
            print("🖐️ Hand Detected") 
            for hand_landmarks in results.multi_hand_landmarks:
                x_, y_, data_aux = [], [], []
                
                # Extract Coordinates
                for lm in hand_landmarks.landmark:
                    x_.append(lm.x)
                    y_.append(lm.y)

                min_x, min_y = min(x_), min(y_)
                for lm in hand_landmarks.landmark:
                    data_aux.append(lm.x - min_x)
                    data_aux.append(lm.y - min_y)
                
                # Predict
                if len(data_aux) == 42:
                    try:
                        prediction = model.predict([np.asarray(data_aux)])
                        predicted_key = prediction[0]
                        print(f"🧠 Raw Model Output: {predicted_key}") 

                        # Smart Lookup (Handles string '0' vs int 0)
                        predicted_character = labels_dict.get(predicted_key)
                        if predicted_character is None:
                             predicted_character = labels_dict.get(int(predicted_key), "Unknown")

                        # Get Confidence
                        try:
                            probs = model.predict_proba([np.asarray(data_aux)])
                            confidence_score = float(np.max(probs)) * 100
                        except:
                            confidence_score = 85.0 # Fallback

                    except Exception as e:
                        print(f"❌ Prediction Logic Error: {e}")
                        predicted_character = "Error"
        else:
            print("🚫 No Hand Found in Frame") 

    except Exception as e:
        print(f"❌ General Error: {e}")
        return jsonify({'prediction': "Error", 'confidence': 0})
    
    return jsonify({'prediction': predicted_character, 'confidence': confidence_score})

if __name__ == '__main__':
    app.run(debug=True)