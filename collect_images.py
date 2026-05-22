import os
import cv2
import time
import string

# --- Configuration ---
DATA_DIR = './data'
DATASET_SIZE = 1000  # UPDATED: Changed from 100 to 1000
CAMERA_INDEX = 1     # Use 0 or 1 depending on your webcam
RESUME_FILE = '.last_label.txt' # File to store the last completed label

# Create the base data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# --- Persistence Functions ---

def get_last_completed_label():
    """Reads the last completed label and type (N/L) from the resume file."""
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, 'r') as f:
            content = f.read().strip().split(',')
            if len(content) == 2:
                return content[0], content[1]
    return None, None

def save_completed_label(label, choice):
    """Saves the currently completed label and type to the resume file."""
    with open(RESUME_FILE, 'w') as f:
        f.write(f'{label},{choice}')

# --- Label Generation ---

def get_labels(choice):
    """Returns the list of labels based on user choice."""
    if choice.upper() == 'N':
        return [str(i) for i in range(10)]
    elif choice.upper() == 'L':
        return list(string.ascii_uppercase)
    return None

# --- User Choice Loop (Menu) ---

def get_user_choice(frame):
    """Displays prompt and waits for user input (N or L) in the webcam window."""
    prompt = 'Press "N" for Numbers or "L" for Letters...'
    while True:
        temp_frame = frame.copy()
        
        # Framing: Text placed at (50, 50) to avoid cutoff
        cv2.putText(temp_frame, prompt, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(temp_frame, 'Press "Q" to Quit', (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
        cv2.imshow('Data Collection Menu', temp_frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('n'):
            return 'N'
        elif key == ord('l'):
            return 'L'
        elif key == ord('q'):
            return 'Q'
            
# --- Main Data Collection Logic ---

def collect_data():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print(f"Error: Could not open webcam with index {CAMERA_INDEX}")
        return

    # 1. Get initial frame for menu
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab initial frame.")
        cap.release()
        return
        
    # 2. Get user choice
    print("\nWaiting for user to choose 'N' (Numbers) or 'L' (Letters)...")
    choice = get_user_choice(frame)
    
    if choice == 'Q':
        print("User quit the application.")
        cap.release()
        cv2.destroyAllWindows()
        return

    labels = get_labels(choice)
    if not labels:
        print("Invalid choice. Exiting.")
        cap.release()
        cv2.destroyAllWindows()
        return
        
    choice_type = 'Numbers (0-9)' if choice == 'N' else 'Letters (A-Z)'
    print(f"Selected: {choice_type}")
    NUMBER_OF_CLASSES = len(labels)
    
    # 3. Check for resumption point
    last_label, last_choice = get_last_completed_label()
    
    start_index = 0
    if last_label and last_choice == choice:
        try:
            start_index = labels.index(last_label) + 1
            if start_index < NUMBER_OF_CLASSES:
                print(f"**Resuming data collection for {choice_type} from label: {labels[start_index]} (after {last_label})**")
            elif start_index == NUMBER_OF_CLASSES:
                 print(f"**Collection for {choice_type} is already complete!**")
        except ValueError:
            print("Resume point found, but label is invalid. Starting from the beginning.")
            start_index = 0
    elif last_label and last_choice != choice:
        print(f"Previous collection was for different type. Starting new collection.")
    else:
        print("Starting collection from the beginning.")

    # 4. Loop through each label
    for i in range(start_index, NUMBER_OF_CLASSES):
        class_label = labels[i]
        class_dir = os.path.join(DATA_DIR, class_label)
        os.makedirs(class_dir, exist_ok=True)

        print(f"\n=== Collecting data for label: {class_label} ({i + 1} of {NUMBER_OF_CLASSES}) ===")

        # Wait for user to press 'q' to begin
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            cv2.putText(frame, f'Current Label: {class_label}', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
            cv2.putText(frame, 'Press "Q" to Start Capturing...', (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Data Collector', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == 27: # Esc
                 print("Collection aborted by user.")
                 cap.release()
                 cv2.destroyAllWindows()
                 return

        print("Starting in 2 seconds... Get ready!")
        time.sleep(2)

        # 5. Capture images
        for img_id in range(DATASET_SIZE):
            
            # --- PAUSE LOGIC START ---
            # Pause after every 100 images (but not at 0)
            if img_id > 0 and img_id % 100 == 0:
                print(f"Paused at {img_id}. Waiting for 'C' to continue...")
                while True:
                    ret, frame = cap.read()
                    if not ret: break

                    # Display Pause UI
                    # Using (50, 150) to ensure it doesn't overlap with other text or get cut off
                    cv2.putText(frame, f'Paused: {img_id}/{DATASET_SIZE} Captured', (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                    cv2.putText(frame, f'Press "C" to Continue', (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                    cv2.imshow('Data Collector', frame)

                    k = cv2.waitKey(1) & 0xFF
                    # Check for 'c' or 'C'
                    if k == ord('c') or k == ord('C'):
                        print("Resuming...")
                        time.sleep(1) # Brief pause before snapping starts again
                        break
                    elif k == 27: # Allow Esc during pause
                        cap.release()
                        cv2.destroyAllWindows()
                        return
            # --- PAUSE LOGIC END ---

            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                continue

            # Save the image
            img_path = os.path.join(class_dir, f'{img_id}.jpg')
            cv2.imwrite(img_path, frame)

            # Display the current frame
            # Framing: Text at (20, 30) and (20, 60) for clear visibility
            cv2.putText(frame, f'Label: {class_label}', (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, f'Capturing {img_id + 1}/{DATASET_SIZE}', (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.imshow('Data Collector', frame)

            if cv2.waitKey(25) & 0xFF == 27: # Esc key
                print(f"Collection for {class_label} stopped mid-capture.")
                cap.release()
                cv2.destroyAllWindows()
                return

        print(f"✅ Finished capturing for label: {class_label}")
        
        # 6. Save the successfully completed label
        save_completed_label(class_label, choice)
        
    # 7. Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("\n📦 Dataset collection completed successfully!")

if __name__ == '__main__':
    collect_data()