import cv2
import mediapipe as mp
import json

# MediaPipe 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,  # 양손 추적
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# 손가락 이름 매핑
finger_names = [
    "WRIST", "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_MCP", "INDEX_PIP", "INDEX_DIP", "INDEX_TIP",
    "MIDDLE_MCP", "MIDDLE_PIP", "MIDDLE_DIP", "MIDDLE_TIP",
    "RING_MCP", "RING_PIP", "RING_DIP", "RING_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    hands_json = []  # 전체 손 데이터 리스트

    if result.multi_hand_landmarks and result.multi_handedness:
        for idx, (hand_landmarks, hand_handedness) in enumerate(zip(result.multi_hand_landmarks, result.multi_handedness)):
            # 시각화
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 각 손 좌표 수집
            landmarks_dict = {}
            for i, lm in enumerate(hand_landmarks.landmark):
                landmarks_dict[finger_names[i]] = [round(lm.x, 4), round(lm.y, 4), round(lm.z, 4)]

            # 손의 방향 (왼손/오른손)
            label = hand_handedness.classification[0].label  # 'Left' or 'Right'

            hands_json.append({
                "index": idx,
                "label": label,
                "landmarks": landmarks_dict
            })

        # JSON 출력
        json_data = json.dumps(hands_json, indent=2)
        print(json_data)

    cv2.imshow("Hand Tracking (Both Hands)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
