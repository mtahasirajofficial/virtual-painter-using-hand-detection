<h1 align="center">🎨 Virtual Painter Using Hand Detection</h1>

<p align="center">
  <b>Paint on a digital canvas with nothing but your fingertips.</b><br>
  An AI-powered virtual painting app that uses real-time hand tracking and gesture recognition to let you draw in the air using only your webcam.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

---

## ✨ Overview

**Virtual Painter** turns your webcam into a touchless drawing tool. Using computer vision and machine-learning-based hand landmark detection, the app tracks your hand in real time and translates finger gestures into brush strokes on a digital canvas — no mouse, no stylus, no touchscreen required.

Raise your index finger to draw, raise two fingers to switch tools or colors, and watch your movements appear instantly on screen. It's a hands-on demonstration of how gesture recognition and real-time pose estimation can power natural, intuitive human–computer interaction.

---

## 🚀 Features

- 🖐️ **Real-Time Hand Detection** — Tracks 21 hand landmarks per frame using Google's MediaPipe.
- ✍️ **Gesture-Based Drawing** — Draw simply by pointing; lift a second finger to pause or select.
- 🎨 **Multiple Brush Colors** — Switch between colors on the fly using a gesture-controlled header menu.
- 🧽 **Eraser Mode** — Clean up mistakes without touching your keyboard.
- 📹 **Live Webcam Canvas** — Your strokes are overlaid directly onto the live video feed.
- ⚡ **Low Latency** — Optimized for smooth, responsive performance on standard hardware.

---

## 🛠️ Tech Stack

| Technology     | Role                                                      |
| -------------- | --------------------------------------------------------- |
| **Python**     | Core application language                                 |
| **OpenCV**     | Video capture, image processing, and canvas rendering     |
| **MediaPipe**  | Real-time hand and finger landmark detection              |
| **NumPy**      | Efficient array operations for the drawing canvas         |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- A working webcam

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/mtahasirajofficial/virtual-painter-using-hand-detection.git

# 2. Move into the project directory
cd virtual-painter-using-hand-detection

# 3. (Recommended) Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 4. Install dependencies
pip install opencv-python mediapipe numpy
```

---

## ▶️ Usage

Run the main script from the project folder:

```bash
python main.py
```

Then:

1. Allow access to your webcam when prompted.
2. Position your hand in front of the camera.
3. **Raise your index finger** to start drawing.
4. **Raise your index + middle fingers** to switch to selection mode (choose colors / eraser).
5. Press **`Q`** (or close the window) to exit.

> 💡 **Tip:** Make sure you're in a well-lit space — good lighting dramatically improves hand-tracking accuracy.

---

## 🎯 How It Works

1. **Capture** — OpenCV grabs frames from the webcam in real time.
2. **Detect** — MediaPipe identifies your hand and maps 21 key landmarks.
3. **Interpret** — The app reads which fingers are up to determine the active gesture (draw, select, erase).
4. **Render** — Finger movements are drawn onto a NumPy canvas, which is blended back onto the live feed.

This pipeline runs every frame, creating the illusion of painting directly in the air.

---

## 📂 Project Structure

```
virtual-painter-using-hand-detection/
└── Virtual Painter Using Hand Detection-Group 04/
    ├── main.py                 # Main application entry point
    ├── HandTrackingModule.py   # Reusable hand-detection helper module
    └── Header/                 # UI assets (color/tool selection bar)
```

---

## 🔮 Future Improvements

- [ ] Adjustable brush thickness via pinch gestures
- [ ] Save artwork directly to an image file
- [ ] Multi-hand and two-handed drawing support
- [ ] Shape recognition (lines, circles, rectangles)
- [ ] Undo / redo functionality

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repo, open an issue, or submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and share it.

---

## 👤 Author

**Muhammad Taha Siraj**

- GitHub: [@mtahasirajofficial](https://github.com/mtahasirajofficial)
- LinkedIn: [mtahasirajofficial](https://www.linkedin.com/in/mtahasirajofficial)

<p align="center">⭐ If you found this project helpful or interesting, consider giving it a star!</p>
