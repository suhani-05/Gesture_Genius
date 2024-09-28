import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
from pynput.keyboard import Controller, Listener

# Initialize MediaPipe Hand and Face Detection
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)
hands = mp_hands.Hands()

# Initialize keyboard controller
keyboard = Controller()

# Get screen size for mouse control
screen_width, screen_height = pyautogui.size()

# Hand Detector Class
class HandDetector:
    def _init_(self, mode=False, maxHands=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw = mp.solutions.drawing_utils
                    self.mpDraw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            h, w, _ = img.shape
            for id, lm in enumerate(myHand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []
        if len(self.lmList) != 0:
            # Thumb
            self.tipIds = [4, 8, 12, 16, 20]
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            # 4 Fingers
            for id in range(1, 5):
                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize hand detector
detector = HandDetector()

# Flag to control whether head movement controls the mouse
head_control_enabled = False

# Function to handle key presses
def on_press(key):
    global head_control_enabled
    try:
        if key.char == 'h' or key.char == 'H':
            head_control_enabled = not head_control_enabled  # Toggle head control on/off
        if key.char == 'g' or key.char == 'G':
            return False  # Terminate the program
    except AttributeError:
        pass

# Start a listener for the keyboard input
listener = Listener(on_press=on_press)
listener.start()

while True:
    success, img = cap.read()
    if not success:
        break

    # Convert the image to RGB for face detection
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect hand gestures
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    fingers = detector.fingersUp()

    # Hand gesture-based keyboard control
    if len(lmList) != 0:
        if fingers[1] == 1:  # Index finger up
            keyboard.release('s')
            keyboard.press("w")  # Press 'W'
        if fingers[1] == 0:  # Index finger down
            keyboard.press("s")
            keyboard.release('w')
        if fingers[0] == 1:  # Thumb up
            keyboard.press("a")  # Press 'A'
        if fingers[0] == 0:  # Thumb down
            keyboard.release('a')
        if fingers[4] == 1:  # Pinky finger up
            keyboard.press('d')  # Press 'D'
        if fingers[4] == 0:  # Pinky finger down
            keyboard.release('d')

    # Head movement-based mouse control (only when head_control_enabled is True)
    if head_control_enabled:
        results = face_detection.process(image_rgb)
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = img.shape
                x1 = int(bboxC.xmin * w)
                y1 = int(bboxC.ymin * h)
                x2 = int((bboxC.xmin + bboxC.width) * w)
                y2 = int((bboxC.ymin + bboxC.height) * h)

                # Draw bounding box around face
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # Calculate the center of the face
                face_center_x = (x1 + x2) // 2

                # Map the face center to the screen coordinates
                mousee_x = np.interp(face_center_x, [0, w], [screen_width, 0])
                mousee_y = np.interp(y1, [0, h], [0, screen_height])
                pyautogui.moveTo(mousee_x, mousee_y)

    # Show the frame
    cv2.imshow("Hand and Head Control", img)

    # Exit on 'q' key (or 'g' key press is handled via the keyboard listener)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
listener.stop()  # Stop the listener after the loop ends

