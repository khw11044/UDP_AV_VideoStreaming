import cv2
from util.streamer import VideoStreamer

def main():
    # VideoStreamer 객체 생성
    video_stream = VideoStreamer(host='0.0.0.0', vs_udp_port=7777)

    try:
        # 영상 스트림 시작
        video_stream.start_video_stream()

        print("Press 'q' to quit the video stream.")
        while True:
            # 최신 프레임 가져오기
            frame = video_stream.frame_reader.latest_frame

            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imshow("Video Stream", frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        video_stream.stop_video_stream()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
