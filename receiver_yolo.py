import cv2
import time
from util.streamer import TelloVideo
import numpy as np 

from ultralytics import YOLO

model = YOLO("yolo11n.pt")
def main():
    # TelloVideo 객체 생성
    video_stream = TelloVideo(host='0.0.0.0', vs_udp_port=7777)
    frame_cnt = 0
    try:
        # 비디오 스트림 시작
        video_stream.start_video_stream()

        print("Press 'q' to quit the video stream.")
        while True:
            # 프레임 읽기
            frame = video_stream.background_frame_read.frame

            # NoneType 프레임 무시
            if frame is None:
                time.sleep(0.01)  # 프레임이 없을 때 잠시 대기
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            results = model.predict(frame, classes=[0])
            
            for result in results:
                for box in result.boxes:
                    x1,y1,x2,y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0, 255, 0), 2)
            
            
            cv2.imshow("Tello Video Stream", frame)

            # 프레임 속도 조절 (옵션)
            time.sleep(0.03)  # 30 FPS로 맞추기 위한 대기 시간

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Stopping video stream...")
                break

    except KeyboardInterrupt:
        print("Video stream interrupted by user.")

    finally:
        # 비디오 스트림 종료
        video_stream.stop_video_stream()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
