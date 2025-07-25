import cv2
import mediapipe as mp
import csv
import time
import os

label = input("label : ")
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
pause = False

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
        display_text = "Recording... Press 'q' to stop\n or Press 'a' to pause"
    elif not recording and pause:
        display_text = "Pause Press 'a' to continue"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            if recording:
                # 좌표 저장
                wrist = hand_landmarks.landmark[0]
                row = []

                # 손바닥 이동량을 포함 (이전 프레임과 비교)
                if len(landmarks_data) > 0:
                    prev_wrist = landmarks_data[-1][:3]
                    move_dx = wrist.x - prev_wrist[0]
                    move_dy = wrist.y - prev_wrist[1]
                    move_dz = wrist.z - prev_wrist[2]
                else:
                    move_dx = move_dy = move_dz = 0.0

                row.extend([move_dx, move_dy, move_dz])  # 3개 좌표 추가

                # 나머지 20개 관절 좌표를 WRIST 기준 상대 좌표로
                for i, lm in enumerate(hand_landmarks.landmark):
                    if i == 0:  # WRIST 자체는 제외
                        continue
                    dx = lm.x - wrist.x
                    dy = lm.y - wrist.y
                    dz = lm.z - wrist.z
                    row.extend([dx, dy, dz])
                landmarks_data.append(row)
            if recording:
                for lm in hand_landmarks.landmark:
                    print(lm.x, lm.y, lm.z, end=' ')
                print()
            # 시각화
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

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
    elif key == ord('a'):
        if recording:
            recording = False
            pause = True
        else:
            recording = True
            pause = False
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
