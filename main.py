import cv2
import mediapipe as mp

# Workaround for X11/Wayland display authority issue with python-xlib on modern Linux.
# Mutter/Wayland Xauthority files use empty display numbers which python-xlib doesn't match by default.
try:
    import Xlib.xauth
    orig_get_best_auth = Xlib.xauth.Xauthority.get_best_auth
    def patched_get_best_auth(self, family, address, dispno, types=(b"MIT-MAGIC-COOKIE-1",)):
        num = str(dispno).encode()
        address = address.encode()
        matches = {}
        for efam, eaddr, enum, ename, edata in self.entries:
            if efam == family and eaddr == address and (num == enum or enum == b'' or enum is None):
                matches[ename] = edata
        for t in types:
            if t in matches:
                return (t, matches[t])
        return orig_get_best_auth(self, family, address, dispno, types)
    Xlib.xauth.Xauthority.get_best_auth = patched_get_best_auth
except ImportError:
    pass

import pyautogui
import time
from mediapipe.tasks.python import vision
import os
import sys

# Resolve the hand landmark model relative to this script so execution is cwd-independent.
# Get the model path
model_path = os.path.join(os.path.dirname(__file__), "models/hand_landmarker.task")

if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    print("Please run: python3 setup_models.py")
    exit(1)

# Configure a single-hand detector tuned for stable real-time tracking.
# Create HandLandmarker with the model
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
hand_landmarker = vision.HandLandmarker.create_from_options(options)

# Open the webcam or video file.
mp_drawing = vision.drawing_utils

# Determine the video source (webcam index, local video file path, or IP camera URL)
video_source = 0
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg.isdigit():
        video_source = int(arg)
    else:
        video_source = arg
        # Bypass local file check for network URLs / IP camera streams
        is_stream = any(video_source.startswith(proto) for proto in ["http://", "https://", "rtsp://", "rtmp://"])
        if not is_stream:
            # Check if it looks like an IP camera address (e.g. 192.168.0.103:4747)
            if ":" in video_source and not video_source.startswith("/") and not video_source.startswith("."):
                if not video_source.endswith("/video") and not video_source.endswith("/mjpegfeed"):
                    video_source = f"http://{video_source}/video"
                else:
                    video_source = f"http://{video_source}"
                print(f"Interpreting network stream URL: {video_source}")
            elif not os.path.exists(video_source):
                print(f"Error: Video file not found at {video_source}")
                sys.exit(1)

cap = cv2.VideoCapture(video_source)

if not cap.isOpened():
    print(f"\nError: Could not open video source '{video_source}'.")
    if video_source == 0:
        print("No physical webcam was detected on your system (no /dev/video* devices found).")
        print("\nTo run gesture control, please either:")
        print(" 1. Connect a physical USB webcam.")
        print(" 2. Use a mobile device as a wireless camera (e.g. via DroidCam or Iriun Webcam).")
        print(" 3. Pass a pre-recorded test video file to the script:")
        print("    python main.py path/to/video.mp4\n")
    sys.exit(1)

from collections import deque

last_time = 0
cooldown = 1.0  # Swipe gestures feel better with a 1.0s cooldown

# History buffer to track hand position for swipe gestures
history = deque(maxlen=20)
one_finger_frames = 0
active_gesture = "Waiting..."
gesture_display_until = 0

def fingers_up(hand_landmarks):
    """Detect which fingers are up based on landmarks"""
    tips = [8, 12, 16, 20]   # Fingertip indices
    pips = [6, 10, 14, 18]   # PIP joint indices

    fingers = []

    for tip, pip in zip(tips, pips):
        # If tip is above pip, finger is up
        if hand_landmarks[tip].y < hand_landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def detect_swipe(history_buf):
    """Analyze hand movement history to detect swipes"""
    if len(history_buf) < 5:
        return None
    
    now = time.time()
    # Filter to coordinates from the last 0.4 seconds
    recent = [pt for pt in history_buf if now - pt[2] <= 0.4]
    
    if len(recent) < 5:
        return None
        
    # Start and end coordinates of recent movement
    start_x, start_y, _ = recent[0]
    end_x, end_y, _ = recent[-1]
    
    dx = end_x - start_x
    dy = end_y - start_y
    
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    
    # Hand must travel at least 18% of the screen dimension
    swipe_threshold = 0.18
    
    # Check if horizontal movement is dominant
    if abs_dx > swipe_threshold and abs_dx > abs_dy * 1.8:
        if dx < 0:
            return "left"
        else:
            return "right"
    # Check if vertical movement is dominant
    elif abs_dy > swipe_threshold and abs_dy > abs_dx * 1.8:
        if dy < 0:
            return "up"
        else:
            return "down"
            
    return None

while True:

    success, frame = cap.read()

    if not success:
        break

    # Mirror the frame so hand movement feels natural to the person on camera.
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Create MediaPipe image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect hand landmarks
    detection_result = hand_landmarker.detect(mp_image)

    current_time = time.time()

    if detection_result.hand_landmarks:

        for hand_landmarks in detection_result.hand_landmarks:
            
            # Draw hand landmarks
            for landmark in hand_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), 1)
            
            # Draw connections between landmarks
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),          # Thumb
                (5, 6), (6, 7), (7, 8),                  # Index
                (9, 10), (10, 11), (11, 12),             # Middle
                (13, 14), (14, 15), (15, 16),            # Ring
                (17, 18), (18, 19), (19, 20),            # Pinky
                (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)  # Palm
            ]
            
            for connection in connections:
                start_idx, end_idx = connection
                start = hand_landmarks[start_idx]
                end = hand_landmarks[end_idx]
                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

            # 1. Handle one-finger exit gesture (close application if held for 12 frames)
            fingers = fingers_up(hand_landmarks)
            total = fingers.count(1)

            if total == 1:
                one_finger_frames += 1
                if one_finger_frames >= 12:
                    print("\nOne finger gesture detected continuously. Closing application...")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit(0)
            else:
                one_finger_frames = 0

            # 2. Track middle-finger MCP landmark (9) for swipe tracking
            hand_center = hand_landmarks[9]
            history.append((hand_center.x, hand_center.y, current_time))

            # 3. Detect and trigger swipes after cooldown
            if current_time - last_time > cooldown:
                swipe = detect_swipe(history)
                if swipe:
                    if swipe == "left":
                        pyautogui.press("right")
                        active_gesture = "Next Slide (Swipe Left)"
                        gesture_display_until = current_time + 1.2
                        last_time = current_time
                        history.clear()
                    elif swipe == "right":
                        pyautogui.press("left")
                        active_gesture = "Previous Slide (Swipe Right)"
                        gesture_display_until = current_time + 1.2
                        last_time = current_time
                        history.clear()
                    elif swipe == "up":
                        pyautogui.press("esc")
                        active_gesture = "Exit Slideshow (Swipe Up)"
                        gesture_display_until = current_time + 1.2
                        last_time = current_time
                        history.clear()
                    elif swipe == "down":
                        if sys.platform.startswith("linux") or sys.platform.startswith("win"):
                            pyautogui.hotkey("ctrl", "f5")
                        else:
                            pyautogui.hotkey("command", "option", "p")
                        active_gesture = "Start Slideshow (Swipe Down)"
                        gesture_display_until = current_time + 1.2
                        last_time = current_time
                        history.clear()
    else:
        # Reset buffers when no hand is in view
        history.clear()
        one_finger_frames = 0

    # Display active gesture on screen
    display_text = active_gesture if current_time < gesture_display_until else "Waiting..."
    cv2.putText(
        frame,
        display_text,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Google Slides Gesture Control", frame)

    # Press q in the preview window to stop the app.
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()