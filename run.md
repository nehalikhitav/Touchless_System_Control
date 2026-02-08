# How to Run and Test Touchless Project

## Prerequisites

- **Python 3.x**
- **Webcam**
- **Operating System**: Windows/macOS/Linux (Code assumes Windows/standard keyboard for some shortcuts)

## Installation

1.  Navigate to the project directory:
    ```bash
    cd c:\Projects\KITS\Touchless-main
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Execute the main script:
    ```bash
    python Casual-Touch.py
    ```
2.  A window showing your webcam feed should appear.
3.  The application will detect one hand and track landmarks.

## Gestures and Controls

| Gesture         | Fingers                   | Description                                                               |
| :-------------- | :------------------------ | :------------------------------------------------------------------------ |
| **Move Cursor** | Index Up                  | Move your index finger to control the mouse cursor.                       |
| **Click**       | Index & Middle Up (Close) | Pinch Index and Middle fingers together (distance < 30) to click.         |
| **Scroll**      | Index & Middle Up (Apart) | Move hand up/down while Index and Middle fingers are up and apart (> 40). |
| **Right Click** | 4 Fingers Up              | Raise Index, Middle, Ring, and Pinky fingers. Hold for brief moment.      |
| **Swipe Left**  | Index & Pinky Up          | "Rock" sign. Hold to trigger `Ctrl + Left Arrow`.                         |
| **Swipe Right** | Thumb & Pinky Up          | "Shaka" sign. Hold to trigger `Ctrl + Right Arrow`.                       |

## Testing

To verify the logic without a webcam, run the automated test script:

```bash
python test_touchless.py
```

This runs unit tests mocking the camera input to verify that:

- Gestures are recognized correctly.
- Mouse/Keyboard commands are triggered appropriate (Mocked).
