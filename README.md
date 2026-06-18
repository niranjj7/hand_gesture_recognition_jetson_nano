# Jetson Nano — Hand Gesture Media Control

Real-time hand-gesture recognition that turns your hand into a touchless remote for **VLC Media Player**. Built for the **NVIDIA Jetson Nano** (also runs on any desktop with a webcam).

A webcam frame is processed with [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker), finger states are derived from the 21 hand landmarks, and the recognized gesture is mapped to a keyboard/media key sent via `pynput`.

## Gestures

| Gesture | Fingers | Action |
|---|---|---|
| Open Palm | 4–5 fingers up | Play / Pause (`Space`) |
| Index Up | index only | Volume Up (`↑`) |
| Victory Sign | index + middle | Volume Down (`↓`) |
| Shaka / Rock On | thumb+pinky **or** index+pinky | Next Track (`media_next`) |
| Thumbs Up / Closed Fist | thumb only **or** no fingers | Previous Track (`media_previous`) |

On-screen overlay shows the current gesture, FPS, and per-frame processing time.

## Files

| File | Purpose |
|---|---|
| `gesture_controller0.py` | Main runnable script. |
| `gesture_controller.ipynb` | Notebook port pinned for **Python 3.6.9** (Jetson Nano JetPack) with dependency checks and unit tests. |
| `final.ipynb` | Full HCI walkthrough notebook: objective, stack, performance targets, environment checks. |
| `hand_landmarker.task` | MediaPipe hand landmark model (~7.8 MB). Auto-downloaded by the script if missing. |

## Requirements

- Python 3.6+ (3.6.9 on Jetson Nano JetPack; pinned versions in `gesture_controller.ipynb`)
- Webcam
- VLC Media Player

```bash
pip install opencv-python mediapipe pynput
```

> On Jetson Nano, install the MediaPipe / OpenCV builds compatible with your JetPack. See the version pins in `gesture_controller.ipynb` (numpy 1.19.5, opencv 4.5.5.64, mediapipe 0.8.10, pynput 1.6.8).

## Usage

```bash
python gesture_controller0.py
```

1. Open VLC and **keep the VLC window focused** (keystrokes go to the active window).
2. Show gestures to the webcam.
3. Controls:
   - `q` — quit
   - `s` — print performance stats
   - close window (X) — quit

If `hand_landmarker.task` is absent, the script downloads it from Google's MediaPipe storage on first run.

## Tuning

- **Detection confidence** — `min_hand_detection_confidence` / `min_tracking_confidence` (default `0.7`) in `gesture_controller0.py`.
- **Cooldowns** — `cooldown_seconds` (1.0 s, Play/Pause + track changes) and `volume_cooldown` (0.2 s, faster volume repeats).
- **Speed on Jetson Nano** — uncomment the `CAP_PROP_FRAME_WIDTH/HEIGHT` lines (~line 105) to drop capture resolution to 640×480 for higher FPS.

## Performance Targets

| Metric | Target |
|---|---|
| Gesture accuracy | > 90 % (controlled lighting) |
| End-to-end latency | low enough for real-time control |

## How It Works

1. Capture frame, flip for mirror view.
2. `HandLandmarker` detects 21 landmarks for one hand.
3. `count_fingers()` returns a `[thumb, index, middle, ring, pinky]` up/down list — thumb via x-axis vs. knuckle, other fingers via tip-above-PIP on the y-axis.
4. The finger pattern maps to a gesture, and a debounced keystroke is sent to the focused window.
