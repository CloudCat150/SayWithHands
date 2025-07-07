from model import build_model
from preprocess import load_data

# 데이터 로드 (클래스 이름도 자동으로 추출됨)
X, y, class_names = load_data("./data", seq_len=30)

# 모델 빌드
model = build_model(input_shape=(30, 63), num_classes=len(class_names))

# 학습
model.fit(X, y, epochs=50, batch_size=4)

# 저장
model.save("models/gesture_model.h5")

# 클래스 이름 저장 (inference에서 사용하도록)
import json
with open("models/class_names.json", "w") as f:
    json.dump(class_names, f)
