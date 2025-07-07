import numpy as np
import os

def get_class_names(data_dir):
    # CSV 파일 이름에서 확장자 제거하고 클래스 이름 리스트 생성
    return sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(data_dir)
        if f.endswith(".csv")
    ])

def load_data(data_dir, seq_len=30):
    class_names = get_class_names(data_dir)
    X, y = [], []

    for label_idx, class_name in enumerate(class_names):
        file_path = os.path.join(data_dir, f"{class_name}.csv")
        data = np.loadtxt(file_path, delimiter=",")

        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)

        if data.shape[0] >= seq_len:
            data = data[:seq_len]
        else:
            padding = np.zeros((seq_len - data.shape[0], data.shape[1]))
            data = np.vstack([data, padding])

        X.append(data)
        y.append(label_idx)

    return np.array(X), np.array(y), class_names
