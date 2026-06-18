import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import time
from pynput.keyboard import Key, Controller

# --- 1. Setup MediaPipe & Keyboard ---
# Using hand landmark detection with file
import os
model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')

# Try to download model if it doesn't exist
if not os.path.exists(model_path):
    print("Downloading hand landmarker model...")
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-tasks/hand_landmarker/hand_landmarker.task"
    try:
        urllib.request.urlretrieve(url, model_path)
        print(f"Model downloaded to {model_path}")
    except Exception as e:
        print(f"Failed to download model: {e}")
        print("Attempting to run without model detection...")

keyboard = Controller()

# Initialize hand landmarker if model exists
detector = None
if os.path.exists(model_path):
    try:
        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        detector = vision.HandLandmarker.create_from_options(options)
        print("Hand landmarker initialized successfully!")
    except Exception as e:
        print(f"Error initializing detector: {e}")
        detector = None

# --- 2. Helper Functions ---

def draw_landmarks(image, hand_landmarks):
    """Draw hand landmarks on image"""
    if not hand_landmarks:
        return
    
    # Draw connections
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
    ]
    
    h, w = image.shape[:2]
    
    # Draw lines (connections)
    for start, end in connections:
        start_point = hand_landmarks[start]
        end_point = hand_landmarks[end]
        x1, y1 = int(start_point.x * w), int(start_point.y * h)
        x2, y2 = int(end_point.x * w), int(end_point.y * h)
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # type: ignore
    
    # Draw circles (landmarks)
    for landmark in hand_landmarks:
        x, y = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(image, (x, y), 4, (255, 0, 0), -1)  # type: ignore

def count_fingers(hand_landmarks):
    """
    Counts how many fingers are 'up'.
    Returns a list of 5 booleans [Thumb, Index, Middle, Ring, Pinky]
    """
    fingers = []
    
    # Landmark indices
    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    
    # 1. Thumb (Check x-coordinate relative to knuckle for right/left logic)
    if hand_landmarks[tips[0]].x > hand_landmarks[tips[0] - 1].x:
        fingers.append(1)  # Thumb open
    else:
        fingers.append(0)

    # 2. Other 4 fingers (Check y-coordinate: Tip higher than Pip joint)
    for id in range(1, 5):
        if hand_landmarks[tips[id]].y < hand_landmarks[tips[id] - 2].y:
            fingers.append(1)  # Finger is open
        else:
            fingers.append(0)
            
    return fingers

# --- 3. Main Loop ---
if detector:
    cap = cv2.VideoCapture(0)  # type: ignore
    
    # Jetson Nano optimization: Set lower resolution for faster processing
    # Uncomment to enable (trades quality for speed)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # type: ignore
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # type: ignore
    
    last_action_time = 0
    cooldown_seconds = 1.0  # Wait 1 second between Play/Pause toggles
    volume_cooldown = 0.2   # Wait 0.2 seconds for volume changes (faster)

    # FPS Counter
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0
    frame_times = []  # For averaging frame times

    print("System Started. Open VLC Media Player and focus the window.")
    print("Commands:")
    print("  OPEN PALM (4-5 fingers) -> Play/Pause")
    print("  INDEX UP -> Volume Up")
    print("  VICTORY SIGN (Index + Middle) -> Volume Down")
    print("  SHAKA SIGN (Thumb + Pinky) or ROCK ON (Index + Pinky) -> Next Track")
    print("  THUMBS UP (Thumb only) -> Previous Track")
    print("  CLOSED FIST (No fingers) -> Previous Track")
    print("\nNote: Press 'q' to exit. Press 's' to print performance stats.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # FPS Counter - Track frame processing time
        frame_start_time = time.time()
        fps_counter += 1

        # Flip frame for mirror view
        frame = cv2.flip(frame, 1)  # type: ignore
        h, w, c = frame.shape

        # Convert frame to MediaPipe Image
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # type: ignore
        detection_result = detector.detect(image)

        gesture_name = "None"

        if detection_result.hand_landmarks:
            for hand_lms in detection_result.hand_landmarks:
                draw_landmarks(frame, hand_lms)
                
                # Analyze Fingers
                fingers_state = count_fingers(hand_lms)
                total_fingers = fingers_state.count(1)
                
                # --- GESTURE LOGIC ---
                
                current_time = time.time()
                
                # Gesture 1: Open Palm (4 or 5 fingers up) -> Play/Pause
                if total_fingers >= 4:
                    gesture_name = "Play/Pause"
                    if current_time - last_action_time > cooldown_seconds:
                        keyboard.press(Key.space)
                        keyboard.release(Key.space)
                        last_action_time = current_time
                        print("Action: Play/Pause")

                # Gesture 2: Index Finger Up Only -> Volume Up
                elif fingers_state == [0, 1, 0, 0, 0] or fingers_state == [1, 1, 0, 0, 0]: 
                    gesture_name = "Volume Up"
                    if current_time - last_action_time > volume_cooldown:
                        # VLC often uses Ctrl+Up or just Up arrow
                        keyboard.press(Key.up)
                        keyboard.release(Key.up)
                        last_action_time = current_time
                        print("Action: Vol Up")

                # Gesture 3: Victory Sign (Index + Middle) -> Volume Down
                elif fingers_state == [0, 1, 1, 0, 0] or fingers_state == [1, 1, 1, 0, 0]:
                    gesture_name = "Volume Down"
                    if current_time - last_action_time > volume_cooldown:
                        keyboard.press(Key.down)
                        keyboard.release(Key.down)
                        last_action_time = current_time
                        print("Action: Vol Down")

                # Gesture 4: Shaka Sign (Thumb + Pinky) or Rock On (Index + Pinky) -> Next Track
                elif fingers_state == [1, 0, 0, 0, 1] or fingers_state == [0, 1, 0, 0, 1]:
                    gesture_name = "Next Track"
                    if current_time - last_action_time > cooldown_seconds:
                        keyboard.press(Key.media_next)
                        keyboard.release(Key.media_next)
                        last_action_time = current_time
                        print("Action: Next Track")

                # Gesture 5: Thumbs Up (Thumb only) or Closed Fist (No fingers up) -> Previous Track
                elif fingers_state == [1, 0, 0, 0, 0] or total_fingers == 0:
                    gesture_name = "Previous Track"
                    if current_time - last_action_time > cooldown_seconds:
                        keyboard.press(Key.media_previous)
                        keyboard.release(Key.media_previous)
                        last_action_time = current_time
                        print("Action: Previous Track")

        # Display Text on Screen
        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 50),  # type: ignore
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # type: ignore

        # Calculate and display FPS
        elapsed_time = time.time() - fps_start_time
        if elapsed_time >= 1.0:  # Update FPS every second
            current_fps = fps_counter / elapsed_time
            fps_counter = 0
            fps_start_time = time.time()
        
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 100),  # type: ignore
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)  # type: ignore

        # Calculate and display frame processing time
        frame_process_time = (time.time() - frame_start_time) * 1000  # Convert to ms
        frame_times.append(frame_process_time)
        if len(frame_times) > 30:
            frame_times.pop(0)
        avg_frame_time = sum(frame_times) / len(frame_times)
        
        cv2.putText(frame, f"Frame: {frame_process_time:.1f}ms (avg: {avg_frame_time:.1f}ms)", (10, 150),  # type: ignore
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)  # type: ignore

        cv2.imshow("Hand Gesture Control", frame)  # type: ignore

        # Exit on 'q' key or print stats on 's' key
        key = cv2.waitKey(1) & 0xFF  # type: ignore
        if key == ord('q'):  # type: ignore
            break
        elif key == ord('s'):
            print(f"\n--- Performance Stats ---")
            print(f"Current FPS: {current_fps:.1f}")
            print(f"Average Frame Time: {avg_frame_time:.1f}ms")
            print(f"Minimum Frame Time: {min(frame_times):.1f}ms")
            print(f"Maximum Frame Time: {max(frame_times):.1f}ms")
            print(f"------------------------\n")
        
        # Check if window was closed by clicking the X button
        if cv2.getWindowProperty("Hand Gesture Control", cv2.WND_PROP_VISIBLE) < 1:  # type: ignore
            break

    cap.release()
    cv2.destroyAllWindows()  # type: ignore
else:
    print("Hand landmarker detector could not be initialized.")
    print("Please ensure the model file is available or can be downloaded.")