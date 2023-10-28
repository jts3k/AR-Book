# AR Book
Tools for a mixed reality presentation system

![Demonstration](./assets/AR-Book.gif)

This repository provides a combined solution for detecting hands using MediaPipe and ArUco markers in live video streams. It includes:

1. A script to detect hands and ArUco markers and send their coordinates over OSC (Open Sound Control).
2. A utility to generate ArUco markers and save them in a PDF for easy printing.

## Installation

### Prerequisites:

- Python 3.7 or newer
- pip

### Steps:

1. Clone this repository:

```bash
git clone https://github.com/jts3k/AR-Book
cd AR-Book
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Hand and ArUco Marker Detection

```bash
python main.py --input CAMERA_INDEX --show DISPLAY_FLAG --ip OSC_IP --port OSC_PORT --inverted
```

Arguments:
- `--input`: Camera input index (default: `0`).
- `--show`: Display the CV2 window (default: `0`).
- `--ip`: IP address for OSC messages (default: `127.0.0.1`).
- `--port`: Port number for OSC messages (default: `8000`).
- `--inverted`: Use this flag to detect inverted markers.

### Generate ArUco Markers PDF

```bash
python aruco_pdf_generator.py N_MARKERS OUTPUT_FILE --dictionary DICTIONARY_NAME --size WIDTH HEIGHT --random --inverted
```

Arguments:
- `N_MARKERS`: Number of markers to generate.
- `OUTPUT_FILE`: Name of the output PDF file.
- `--dictionary`: ArUco marker dictionary (default: `DICT_6X6_250`).
- `--size`: Size of each marker in millimeters (default: `100 100`).
- `--random`: Use this flag to generate random markers.
- `--inverted`: Use this flag to generate inverted markers.

## Dependencies

These are the primary libraries used in this project:

- `cv2`: For video processing and ArUco marker generation.
- `mediapipe`: For hand detection.
- `pythonosc`: For sending data over OSC.
- `PIL` and `fpdf`: For generating a PDF of ArUco markers.

Ensure all dependencies are installed using the `requirements.txt` file.
