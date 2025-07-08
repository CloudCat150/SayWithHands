import cv2
import mediapipe as mp
import numpy as np
import json
import tensorflow as tf

from model import build_model


# 클래스 이름 불러오기
with open("models/class_names.json", "r") as f:
    class_names = json.load(f)

# 모델 생성 및 가중치 로드
model = build_model(input_shape=(30, 63), num_classes=len(class_names))
model.load_weights("models/gesture_model.h5")

# MediaPipe 및 웹캠 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()
sequence = []
seq_len = 30

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        row = []
        for lm in hand_landmarks.landmark:
            row.extend([lm.x, lm.y, lm.z])
        sequence.append(row)

        if len(sequence) > seq_len:
            sequence.pop(0)

        if len(sequence) == seq_len:
            input_data = np.expand_dims(sequence, axis=0)
            pred = model.predict(input_data)
            class_id = np.argmax(pred)
            confidence = pred[0][class_id]

            if confidence > 0.7:
                print(f"Predicted gesture: {class_names[class_id]} ({confidence:.2f})")
        
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Recognition", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
