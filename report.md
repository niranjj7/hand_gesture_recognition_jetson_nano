# Import Report — Hand Gesture Recognition (Jetson Nano)

**Date:** 2026-06-18

## Summary

The contents of the project **Jetson Nano — Hand Gesture Media Control** were
imported into this repository (`niranjj7/hand_gesture_recognition_jetson_nano`)
from the upstream source repository.

## Source

- **Upstream repo:** https://github.com/AlanThomasPaul/Jetson_nano-hand_gestures
- **Imported via:** `Jetson_nano-hand_gestures-main.zip` (a download of the upstream `main` branch)

## What this project does

Real-time hand-gesture recognition that turns a hand into a touchless remote for
VLC Media Player, targeting the NVIDIA Jetson Nano (also runs on any desktop with
a webcam). A webcam frame is processed with MediaPipe Hands; finger states are
derived from the 21 hand landmarks, and the recognized gesture is mapped to a
media/keyboard key sent via `pynput`.

| Gesture | Action |
|---|---|
| Open Palm | Play / Pause |
| Index Up | Volume Up |
| Victory Sign | Volume Down |
| Shaka / Rock On | Next Track |
| Thumbs Up / Closed Fist | Previous Track |

## Files imported

| File | Purpose |
|---|---|
| `gesture_controller0.py` | Main runnable script. |
| `gesture_controller.ipynb` | Notebook port pinned for Python 3.6.9 (Jetson Nano JetPack). |
| `final.ipynb` | Full HCI walkthrough notebook. |
| `hand_landmarker.task` | MediaPipe hand landmark model (~7.8 MB). |
| `README.md` | Project documentation. |
| `.gitattributes` | LF normalization. |

## Attribution

Original work by [AlanThomasPaul](https://github.com/AlanThomasPaul/Jetson_nano-hand_gestures).
This repository is a copy/import for personal use.
