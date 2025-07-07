import cv2
import mediapipe as mp
import csv
import time
import os

label = "rock"
save_dir = "./data"
os.makedirs(save_dir, exist_ok=True)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

landmarks_data = []
recording = False
countdown = False
countdown_start = 0

print("q 눌러서 녹화 시작/중지 (녹화 시작 전 3초 카운트다운)")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    display_text = "Press 'q' to start recording"
    if countdown:
        elapsed = time.time() - countdown_start
        remain = 3 - int(elapsed)
        if remain > 0:
            display_text = f"Recording starts in {remain}..."
        else:
            countdown = False
            recording = True
            display_text = "Recording..."
    elif recording:
        display_text = "Recording... Press 'q' to stop."

    # 시각화
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            if recording:
                # 좌표 저장
                row = []
                for lm in hand_landmarks.landmark:
                    row.extend([lm.x, lm.y, lm.z])
                landmarks_data.append(row)

            # 화면에 그리기
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0,128,255), thickness=2)
            )

    cv2.putText(frame, display_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("MediaPipe Hands Recorder", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        if not recording and not countdown:
            countdown = True
            countdown_start = time.time()
        elif recording:
            with open(os.path.join(save_dir, f"{label}.csv"), "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(landmarks_data)
            print(f"Data saved to {os.path.join(save_dir, f'{label}.csv')}")
            break
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
