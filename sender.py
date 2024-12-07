import cv2
import socket
import time
import threading

class VideoStreamer:
    """웹캠 영상을 UDP로 실시간 송신하는 클래스"""
    def __init__(self, target_ip: str, target_port: int, webcam_id: int = 0, fps: int = 30):
        """
        Args:
            target_ip (str): 수신 측 IP 주소
            target_port (int): 수신 측 UDP 포트
            webcam_id (int): 사용할 웹캠 ID (기본 0)
            fps (int): 송신 프레임 속도 (초당 프레임 수)
        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.webcam_id = webcam_id
        self.fps = fps
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]  # 영상 품질 (0~100)

        # 프레임 전송 시간 제어
        self.frame_interval = 1.0 / fps
        self.last_frame_time = time.time()

    def start_stream(self):
        """웹캠 영상 캡처 및 UDP 송신 시작"""
        self.running = True
        cap = cv2.VideoCapture(self.webcam_id)

        if not cap.isOpened():
            print("Error: Unable to open webcam.")
            return

        print(f"Streaming video to {self.target_ip}:{self.target_port} at {self.fps} FPS")

        try:
            while self.running:
                # 현재 시간 기록
                current_time = time.time()

                # FPS 조절: 일정 시간 간격(frame_interval)이 지날 때만 프레임 전송
                if current_time - self.last_frame_time >= self.frame_interval:
                    ret, frame = cap.read()
                    if not ret:
                        print("Error: Failed to capture frame.")
                        continue

                    # 프레임을 JPEG로 압축
                    _, buffer = cv2.imencode('.jpg', frame, self.encode_param)

                    # UDP를 통해 압축된 프레임 데이터 전송
                    self.sock.sendto(buffer.tobytes(), (self.target_ip, self.target_port))

                    # 마지막 전송 시간 갱신
                    self.last_frame_time = current_time

        except KeyboardInterrupt:
            print("Streaming stopped by user.")
        finally:
            cap.release()
            self.sock.close()
            print("Video stream stopped.")

    def stop_stream(self):
        """송신 중지"""
        self.running = False

if __name__ == "__main__":
    # 수신 측 IP와 포트 설정
    TARGET_IP = "172.30.1.31"   # 드론이나 수신 장치의 IP 주소
    TARGET_PORT = 7777          # 수신 포트 (dji.py의 TelloVideo 포트와 일치해야 함)
    FPS = 30                    # 전송할 프레임 속도 (초당 30 프레임)

    # 송신 객체 생성 및 시작
    streamer = VideoStreamer(target_ip=TARGET_IP, target_port=TARGET_PORT, fps=FPS)

    try:
        streamer.start_stream()
    except KeyboardInterrupt:
        streamer.stop_stream()
