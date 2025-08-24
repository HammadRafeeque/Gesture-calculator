import cv2
import numpy as np
import mediapipe as mp
import math
import time

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Calculator button class
class Button:
    def __init__(self, pos, text, size=[60, 60]):
        self.pos = pos
        self.text = text
        self.size = size

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x + w, y + h), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, self.pos, (x + w, y + h), (200, 200, 200), 2)
        cv2.putText(img, self.text, (x + 20, y + 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    def is_clicked(self, x, y):
        bx, by = self.pos
        bw, bh = self.size
        return bx < x < bx + bw and by < y < by + bh

# Calculator button layout
button_texts = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']
]
buttons = []
for i in range(4):
    for j in range(4):
        buttons.append(Button([100 * j + 50, 100 * i + 150], button_texts[i][j]))

# Variables
equation = ''
delay_counter = 0
clicked = False

# OpenCV camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    lm_list = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Draw buttons
    for button in buttons:
        button.draw(img)

    # Logic for clicking
    if lm_list:
        x1, y1 = lm_list[8]  # Index finger tip
        x2, y2 = lm_list[12]  # Middle finger tip

        distance = math.hypot(x2 - x1, y2 - y1)
        cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)

        if distance < 40 and not clicked:
            for button in buttons:
                if button.is_clicked(x1, y1):
                    clicked = True
                    value = button.text
                    if value == 'C':
                        equation = ''
                    elif value == '=':
                        try:
                            equation = str(eval(equation))
                        except:
                            equation = 'Error'
                    else:
                        equation += value
                    break

    # Debounce logic
    if clicked:
        delay_counter += 1
        if delay_counter > 10:
            delay_counter = 0
            clicked = False

    # Display equation/result
    cv2.rectangle(img, (50, 50), (450, 120), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, equation, (60, 110),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv2.imshow("Touchless Calculator", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
