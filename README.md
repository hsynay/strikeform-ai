# StrikeForm AI ⚽🤖

**AI-Driven Shooting Biometrics for Youth Football Academies**

StrikeForm AI is a computer vision-based diagnostic tool designed to prevent chronic knee injuries and improve shooting technique in grassroots football. By utilizing Google's MediaPipe and 3D vector mathematics, it provides amateur coaches with accessible, high-precision biomechanical feedback using just a standard video feed.

## 🎯 The Double Goal
1. **Reduce Injuries:** Detects "Locked Knee" or "Knee Collapse" forms that cause extreme stress on joints and ACLs.
2. **Improve Technique:** Analyzes torso inclination to prevent "Leaning Back" (which causes the ball to fly over the crossbar) or "Over-Leaning" (power loss).

## ✨ Key Features
* **3D Vector Mathematics:** Calculates actual joint angles using the 3D Cosine Theorem (incorporating the Z-axis depth) to eliminate perspective errors from 2D camera angles.
* **Dynamic Support Leg Detection:** Automatically compares ankle Y-coordinates to determine which leg is planted on the ground, adapting instantly to left or right-footed strikes.
* **Interactive Freeze-Frame Analysis:** Runs the AI processing only when the user pauses the video at the *Moment of Impact*. This ensures maximum accuracy and saves CPU processing power.
* **Biomechanical Thresholds:** Hardcoded with scientific joint angle thresholds (e.g., 145°-165° for the support knee) to trigger specific, actionable feedback on the screen.

## 🛠️ Tech Stack
* **Python 3**
* **OpenCV:** For video processing, interactive UI, and rendering the 1920x1080 letterbox canvas.
* **MediaPipe Pose:** For extracting 33 high-fidelity 3D skeletal landmarks.
* **NumPy:** For vector dot-product calculations.

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/hsynay/strikeform-ai.git](https://github.com/hsynay/strikeform-ai.git)
   cd strikeform-ai
   

2. Install the required dependencies:
   ```bash
   pip install opencv-python mediapipe numpy

3. Add your video:

   Place your training video (e.g., Messi_training.mp4) in the root directory and update the video_path variable in the code.

5. Run the script:
   ```Bash
   python main.py


🎮 Interactive Controls

[SPACE] : Pause the video at the exact moment the player strikes the ball to run the AI analysis. Press again to resume the video.

[ESC] : Exit the application.


👨‍💻 About
Developed by Hüseyin Ay as part of the CEN 316 - Technical English coursework. The project demonstrates the translation of sports science into accessible software engineering solutions.

“Fix your form. Maybe you can play for Barcelona!”
