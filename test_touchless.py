import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib.util

# Mock dependencies before importing the module
sys.modules['HandTrackingModule'] = MagicMock()
sys.modules['cv2'] = MagicMock() # Mock OpenCV
# Mock pyautogui but keep it available for assertions
mock_pyautogui = MagicMock()
sys.modules['pyautogui'] = mock_pyautogui

# Helper to import the modified script
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import Casual-Touch
file_path = os.path.join(os.path.dirname(__file__), 'Casual-Touch.py')
casual_touch = import_from_path('CasualTouch', file_path)

class TestTouchlessFeatures(unittest.TestCase):
    def setUp(self):
        self.controller = casual_touch.TouchlessController()
        self.controller.detector = MagicMock()
        # Default behavior for findDistance (return large length to avoid accidental clicks)
        self.controller.detector.findDistance.return_value = (100, MagicMock(), [0, 0, 0, 0, 0, 0])
        # Ensure config matches defaults
        self.controller.wScr = 1920
        self.controller.hScr = 1080
        # Reset mocks
        mock_pyautogui.reset_mock()
        
    def test_move_cursor(self):
        """Test if cursor move logic calculates coordinates and calls moveTo."""
        # Fingers: Index (1) up, others down
        fingers = [0, 1, 0, 0, 0]
        # Coordinates: x1, y1 (Index tip)
        x1, y1 = 200, 200
        x2, y2 = 0, 0 # Middle finger, irrelevant for move
        img = MagicMock()

        # Mock time to ensure gesture activates
        with patch('time.time') as mock_time:
            # First call to activate state
            mock_time.return_value = 1000.0
            self.controller.processGesture(fingers, x1, y1, x2, y2, img)
            
            # Second call after hold time (0.8s) - but wait!
            # The logic for "move" uses updateGestureState?
            # Code: if updateGestureState("move", ...):
            # updateGestureState logic:
            # if condition:
            #   if not active: active=True; start=now
            #   elif now - start >= hold: start=now; return True
            
            # So first call only sets active. Returns False.
            # verify moveTo NOT called
            mock_pyautogui.moveTo.assert_not_called()
            
            # Second call, time advanced
            mock_time.return_value = 1000.0 + 1.0 # > 0.8
            self.controller.processGesture(fingers, x1, y1, x2, y2, img)
            
            # Now it should be called
            mock_pyautogui.moveTo.assert_called()
            
    def test_click(self):
        """Test click logic."""
        # Fingers: Index (1) and Middle (1) up
        fingers = [0, 1, 1, 0, 0]
        x1, y1 = 0, 0 
        x2, y2 = 0, 0
        img = MagicMock()
        
        # Mock detector.findDistance to return small length (<30)
        # return length, img, lineInfo
        self.controller.detector.findDistance.return_value = (20, img, [0]*6)
        
        with patch('time.time') as mock_time:
            mock_time.return_value = 2000.0
            
            # processGesture
            self.controller.processGesture(fingers, x1, y1, x2, y2, img)
            
            # Logic check:
            # if fingers[1]&[2]:
            #   dist < 30
            #   time - lastClickTime (> cooldown 1.0) (lastClickTime init 0) -> True
            #   currentTime (2000) - gestureStates["click"]["startTime"] (0) >= 0.5 -> True
            # Expect click
            mock_pyautogui.click.assert_called()
            
    def test_scroll(self):
        """Test scroll logic."""
        fingers = [0, 1, 1, 0, 0]
        # Distance >= 40
        self.controller.detector.findDistance.return_value = (50, MagicMock(), [0]*6)
        
        # y1 (index) vs y2 (middle)
        # scroll = (y1 - y2) / speed
        # To scroll up/down, need difference
        y1 = 100
        y2 = 200 # y1 < y2. 100 - 200 = -100. scroll = -10.
        
        self.controller.processGesture(fingers, 0, y1, 0, y2, MagicMock())
        
        mock_pyautogui.scroll.assert_called_with(-10)

    def test_right_click(self):
        """Test right click logic."""
        # Fingers: 1, 2, 3, 4 up. Thumb (0) doesn matter?
        # Code: all(fingers[i] == 1 for i in range(1, 5)) -> Index, Middle, Ring, Pinky
        fingers = [0, 1, 1, 1, 1]
        
        with patch('time.time') as mock_time:
            mock_time.return_value = 3000.0
            # First call activates
            self.controller.processGesture(fingers, 0, 0, 0, 0, MagicMock())
            mock_pyautogui.rightClick.assert_not_called()
            
            # Wait
            mock_time.return_value = 3000.0 + 1.0
            self.controller.processGesture(fingers, 0, 0, 0, 0, MagicMock())
            mock_pyautogui.rightClick.assert_called()

    def test_swipe_left(self):
        """Test swipe left gesture."""
        # Fingers: Index(1) & Pinky(1). Thumb(0)??
        # Code: fingers[1]==1 and fingers[4]==1 and fingers[0]==0 and fingers[2]==0 and fingers[3]==0
        fingers = [0, 1, 0, 0, 1]
        
        with patch('time.time') as mock_time:
            mock_time.return_value = 4000.0
            self.controller.processGesture(fingers, 0,0,0,0, MagicMock())
            
            mock_time.return_value = 4000.0 + 1.0
            self.controller.processGesture(fingers, 0,0,0,0, MagicMock())
            
            mock_pyautogui.hotkey.assert_called_with('ctrl', 'left')

if __name__ == '__main__':
    unittest.main()
