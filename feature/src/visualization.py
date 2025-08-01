import cv2
import mediapipe as mp
import json
import os
import time

# MediaPipe 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

finger_names = [
    "WRIST", "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_MCP", "INDEX_PIP", "INDEX_DIP", "INDEX_TIP",
    "MIDDLE_MCP", "MIDDLE_PIP", "MIDDLE_DIP", "MIDDLE_TIP",
    "RING_MCP", "RING_PIP", "RING_DIP", "RING_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
]

frame_path = "C:/Users/user/Desktop/SayWithHands/server/frame/frame.jpg"
last_modified = 0

while True:
    if os.path.exists(frame_path):
        modified_time = os.path.getmtime(frame_path)
        if modified_time != last_modified:
            last_modified = modified_time

            frame = cv2.imread(frame_path)
            if frame is None:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            hands_json = []

            if result.multi_hand_landmarks and result.multi_handedness:
                for idx, (hand_landmarks, hand_handedness) in enumerate(zip(result.multi_hand_landmarks, result.multi_handedness)):
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    landmarks_dict = {}
                    for i, lm in enumerate(hand_landmarks.landmark):
                        landmarks_dict[finger_names[i]] = [round(lm.x, 4), round(lm.y, 4), round(lm.z, 4)]

                    label = hand_handedness.classification[0].label

                    hands_json.append({
                        "index": idx,
                        "label": label,
                        "landmarks": landmarks_dict
                    })

                json_data = json.dumps(hands_json, indent=2)
                print(json_data)

            cv2.imshow("UDP Frame Hand Tracking", frame)
    else:
        print("fames 인식 불가!")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.03)  # 너무 빠른 루프 방지

cv2.destroyAllWindows()
