# Gesture Control Presenter 🎮🖐️

Control your Google Slides and PowerPoint presentations using natural hand gestures in the air, powered by AI and Computer Vision.

This project maps hand movement trajectories and shapes to standard slideshow shortcuts:

* **Swipe Left ⬅️** $\rightarrow$ Next Slide
* **Swipe Right ➡️** $\rightarrow$ Previous Slide
* **Swipe Down ⬇️** $\rightarrow$ Start Presentation
* **Swipe Up ⬆️** $\rightarrow$ Exit Presentation
* **One Finger ☝️** $\rightarrow$ Close Python Script

---

# 🚀 Features

* **Dynamic Swipe Recognition**: Tracks hand position history and velocity over time to identify distinct directional swipes (Left, Right, Up, Down).
* **Return Stroke Filtering & Cooldown**: Automatically filters out return hand movements to prevent accidental duplicate actions.
* **Flexible Camera Support**: Connects to your standard laptop webcam, external USB camera, or mobile device camera (via DroidCam IP stream).
* **Robust Window Manager Support**: Includes automated display authority resolution to support modern Wayland/Mutter desktops out of the box.
* **Persistent Visual Feedback**: Displays the last recognized gesture directly on the video stream window for `1.2` seconds.
* **Safety Exit Gesture**: Detects a single finger held up continuously for `0.4` seconds to safely terminate the script.

---

# 🧠 Gesture Controls

### 🖐️ Right Hand: Presentation Controls
| Gesture | Action | Description |
| :--- | :--- | :--- |
| **Swipe Left** ⬅️ | **Next Slide** | Swipe your hand from right to left across the screen |
| **Swipe Right** ➡️ | **Previous Slide** | Swipe your hand from left to right across the screen |
| **Swipe Up** ⬆️ | **Exit Slideshow** | Swipe your hand upwards |
| **Swipe Down** ⬇️ | **Start Slideshow** | Swipe your hand downwards |

### 🤚 Left Hand: Volume & Zoom Controls
| Gesture | Action | Description |
| :--- | :--- | :--- |
| **2 Fingers Up** + **Move Up** ⬆️ | **Volume Up** | Hold up 2 fingers (Index + Middle) and move your hand upwards |
| **2 Fingers Up** + **Move Down** ⬇️ | **Volume Down** | Hold up 2 fingers (Index + Middle) and move your hand downwards |
| **3 Fingers Up** + **Move Up** ⬆️ | **Zoom In** | Hold up 3 fingers (Index + Middle + Ring) and move your hand upwards |
| **3 Fingers Up** + **Move Down** ⬇️ | **Zoom Out** | Hold up 3 fingers (Index + Middle + Ring) and move your hand downwards |

### ☝️ Either Hand: Safety Exit
| Gesture | Action | Description |
| :--- | :--- | :--- |
| **1 Finger Up** | **Close Script** | Hold up 1 finger continuously for ~0.4s to close the Python app |

---

# 🛠️ Technologies Used

* **Python 3.10+**: Core scripting language.
* **OpenCV (opencv-python)**: Video capture, frame flipping, visual overlay rendering, and window management.
* **MediaPipe**: Real-time hand landmarks tracking model.
* **PyAutoGUI & Python-Xlib**: Automated keyboard shortcut injection.
* **Bash & Windows Batch**: Installer automation scripts.

---

# 📦 Installation & Setup

## Option A: Automated Installation (Recommended)

Run the automated installer script to set up the virtual environment, install package dependencies, and download required models in one go.

* **On Linux/macOS:**
  ```bash
  chmod +x install.sh
  ./install.sh
  ```
* **On Windows:**
  Double-click `install.bat` or run it from the command line:
  ```cmd
  install.bat
  ```

---

## Option B: Manual Setup

If you prefer to configure the environment yourself:

### 1. Create and Activate Virtual Environment
```bash
# Create the environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows Command Prompt)
venv\Scripts\activate.bat
```

### 2. Install Dependencies & Download Models
```bash
# Install packages
pip install -r requirements.txt

# Download MediaPipe model
python setup_models.py
```

---

# ▶️ Run the App

1. Ensure the virtual environment is active:
   ```bash
   source venv/bin/activate
   ```

2. Start the application with your preferred video source:

   * **Webcam (Default):**
     ```bash
     python main.py
     ```

   * **DroidCam IP Stream:**
     ```bash
     python main.py 192.168.0.103:4747
     ```

   * **Custom Video File:**
     ```bash
     python main.py path/to/video.mp4
     ```

---

# 💻 macOS Permission Setup

For keyboard control to work on macOS:

Go to:

System Settings → Privacy & Security

Enable permissions for:

* Accessibility
* Input Monitoring

Allow access for:

* Terminal
  OR
* VS Code
  OR
* PyCharm

Without these permissions, the app cannot control Google Slides.

---

# 🎯 How to Use

1. Open Google Slides in Chrome
2. Start slideshow mode
3. Run the Python application
4. Show gestures in front of webcam
5. Control slides hands-free

---

# 📂 Project Structure

```bash
gesture-control/
│
├── .gitignore
├── install.sh         # Linux/macOS automated installer
├── install.bat        # Windows automated installer
├── main.py            # Main application entry point
├── README.md
├── requirements.txt   # Python package dependencies
├── setup_models.py    # Downloads MediaPipe model assets
└── models/
    └── hand_landmarker.task
```

---

# 📜 requirements.txt

```txt
mediapipe==0.10.35
opencv-python>=4.8.0
pyautogui>=0.9.54
```

---

# 🧩 How It Works

The application operates in five sequential stages:

1. **Video Ingestion**: Captures real-time frames from your webcam, IP camera (DroidCam), or a pre-recorded file using OpenCV.
2. **Hand Tracking**: MediaPipe Hand Landmarker tracks 21 distinct 3D landmarks on your hand at 30+ FPS.
3. **Display Authority Matching**: Before connecting, the script dynamically patches the `python-xlib` library to support Mutter/Wayland Xauthority wildcards (empty display numbers) for modern Linux environments.
4. **Trajectory & Shape Analysis**: 
   * **Swipes**: Tracks the coordinates of your palm center (Middle Finger MCP) over a sliding history window. If the hand moves rapidly in a dominant direction (Left/Right/Up/Down) covering more than 18% of the screen dimension, a swipe event is detected.
   * **Shutdown**: Analyzes finger extension using joint coordinates. If only 1 finger is up continuously for 12 frames, a clean exit is triggered.
5. **Action Dispatching**: Dispatches simulated OS-level keyboard events using PyAutoGUI to control your slides.

---

# 🔮 Future Improvements

* Gesture-based laser pointer
* AI-powered custom gesture training

---

# 🎓 Learning Outcomes

This project helps students understand:

* Computer Vision
* AI-based gesture recognition
* Human Computer Interaction (HCI)
* Real-time webcam processing
* Automation using Python

---

# 📸 Demo Idea

Use this project during:

* AI Workshops
* Hackathons
* College Tech Fests
* Computer Vision Sessions
* Smart Classroom Demonstrations

---

# ⚠️ Notes

* Ensure good lighting conditions
* Keep hand visible to webcam
* Avoid cluttered backgrounds for better detection
* Works best at moderate camera distance

---

# Live MediaPipe 
![MediaPipe Hand Tracking Demo] (https://google-ai-edge.github.io/mediapipe-samples-web/#/vision/hand_landmarker)

![Google AI Media Pipe] (https://ai.google.dev/edge/mediapipe/solutions/guide)

---

# 👨‍💻 Built With AI + Computer Vision

A futuristic interaction system powered by hand tracking and real-time gesture recognition.