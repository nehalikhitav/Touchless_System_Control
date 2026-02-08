import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui
class TouchlessController:
    def __init__(self):
        # Configuration Parameters
        self.wCam, self.hCam = 640, 480
        self.frameR = 100  # Reduced the active region size to prevent false positives
        self.smoothening = 4
        self.clickCooldown = 1.0  # Increased cooldown period
        self.clickHoldTime = 0.5  # Time to hold fingers for click
        self.gestureHoldTime = 0.8  # Time to hold gesture before it's recognized
        self.scrollSpeed = 10

        # Initialize Variables
        self.pTime = 0
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.lastClickTime = 0

        self.gestureStates = {
            "move": {"startTime": 0, "active": False},
            "click": {"startTime": 0, "active": False},
            "scroll": {"startTime": 0, "active": False},
            "rightClick": {"startTime": 0, "active": False},
            "swipeLeft": {"startTime": 0, "active": False},
            "swipeRight": {"startTime": 0, "active": False},
        }

        self.detector = htm.handDetector(maxHands=1)
        try:
            self.wScr, self.hScr = pyautogui.size()
        except:
            self.wScr, self.hScr = 1920, 1080 # Default for testing/headless

    def updateGestureState(self, gestureName, condition):
        currentTime = time.time()
        if condition:
            if not self.gestureStates[gestureName]["active"]:
                self.gestureStates[gestureName]["startTime"] = currentTime
                self.gestureStates[gestureName]["active"] = True
            elif currentTime - self.gestureStates[gestureName]["startTime"] >= self.gestureHoldTime:
                self.gestureStates[gestureName]["startTime"] = currentTime
                return True
        else:
            self.gestureStates[gestureName]["active"] = False
        return False

    def processGesture(self, fingers, x1, y1, x2, y2, img):
        # Move cursor
        if self.updateGestureState("move", fingers[1] == 1 and all(fingers[i] == 0 for i in range(2, 5))):
            x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
            y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))
            self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
            self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening
            
            try:
                pyautogui.moveTo(self.wScr - self.clocX, self.clocY)
            except pyautogui.FailSafeException:
                pass
                
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            self.plocX, self.plocY = self.clocX, self.clocY

        # Click
        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = self.detector.findDistance(8, 12, img)
            if length < 30 and (time.time() - self.lastClickTime) > self.clickCooldown:
                currentTime = time.time()
                if currentTime - self.gestureStates["click"]["startTime"] >= self.clickHoldTime:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
                    self.lastClickTime = time.time()
            elif length >= 40:
                scroll_amount = int((y1 - y2) / self.scrollSpeed)
                if abs(scroll_amount) > 0:
                    pyautogui.scroll(scroll_amount)

        # Right Click
        if self.updateGestureState("rightClick", all(fingers[i] == 1 for i in range(1, 5))):
            pyautogui.rightClick()
            time.sleep(1)

        # Swipe Left (Ctrl + Left Arrow)
        if self.updateGestureState("swipeLeft",
                              fingers[1] == 1 and fingers[4] == 1 and all(fingers[i] == 0 for i in range(0, 1)) and all(
                                      fingers[i] == 0 for i in range(2, 4))):
            pyautogui.hotkey('ctrl', 'left')
            time.sleep(1)

        # Swipe Right (Ctrl + Right Arrow)
        if self.updateGestureState("swipeRight",
                              fingers[0] == 1 and fingers[4] == 1 and all(fingers[i] == 0 for i in range(1, 4))):
            pyautogui.hotkey('ctrl', 'right')
            time.sleep(1)

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, self.wCam)
        cap.set(4, self.hCam)

        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture image")
                continue

            img = self.detector.findHands(img)
            lmList, bbox = self.detector.findPosition(img)

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]
                fingers = self.detector.fingersUp()
                cv2.rectangle(img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR), (255, 0, 255), 2)

                # Process gestures
                self.processGesture(fingers, x1, y1, x2, y2, img)

            # Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            # Display
            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = TouchlessController()
    controller.run()
