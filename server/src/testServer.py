import socket
import threading

# UDP: 영상 수신
def udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 9999))
    while True:
        data, addr = sock.recvfrom(65536)
        with open("frame.jpg", "wb") as f:
            f.write(data)

# TCP: 텍스트 + mp3 전송
def tcp_sender():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(1)
    print("TCP 서버 대기 중...")
    conn, addr = server.accept()
    print("클라이언트 연결됨:", addr)

    while True:
        text = "서버에서 온 메시지입니다."
        audio_data = open("sound.mp3", "rb").read()

        conn.send(len(text.encode()).to_bytes(4, 'big'))
        conn.send(text.encode())

        conn.send(len(audio_data).to_bytes(4, 'big'))
        conn.send(audio_data)

        time.sleep(5)

threading.Thread(target=udp_receiver).start()
threading.Thread(target=tcp_sender).start()
