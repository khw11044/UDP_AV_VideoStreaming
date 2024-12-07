# coding=utf-8
import logging
import socket
from threading import Thread, Lock
from typing import Optional
import av
import numpy as np

class VideoStreamException(Exception):
    """비디오 스트림 관련 예외 클래스"""
    pass

class VideoStreamer:
    """영상 스트림을 수신하고 PyAV를 사용해 프레임을 읽어오는 범용 클래스"""

    # 비디오 스트림 관련 설정
    VS_UDP_IP = '0.0.0.0'
    DEFAULT_VS_UDP_PORT = 8899
    FRAME_GRAB_TIMEOUT = 5  # 프레임 수신 타임아웃

    # 로깅 설정
    HANDLER = logging.StreamHandler()
    FORMATTER = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
    HANDLER.setFormatter(FORMATTER)
    LOGGER = logging.getLogger('video_streamer')
    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.INFO)

    def __init__(self, host: str = VS_UDP_IP, vs_udp_port: int = DEFAULT_VS_UDP_PORT):
        self.host = host
        self.vs_udp_port = vs_udp_port
        self.stream_on = False
        self.frame_reader: Optional['FrameReader'] = None
        self.LOGGER.info("VideoStreamer initialized. Host: '{}', Port: '{}'".format(self.host, self.vs_udp_port))

    def get_udp_video_address(self) -> str:
        """영상 스트림 UDP 주소 반환"""
        address_schema = 'udp://@{ip}:{port}'
        return address_schema.format(ip=self.VS_UDP_IP, port=self.vs_udp_port)

    def start_video_stream(self):
        """영상 스트림 수신 시작"""
        if self.frame_reader is None:
            address = self.get_udp_video_address()
            self.frame_reader = FrameReader(address)
            self.frame_reader.start()
            self.stream_on = True
            self.LOGGER.info("Video stream started.")
        else:
            self.LOGGER.info("Video stream is already running.")

    def stop_video_stream(self):
        """영상 스트림 수신 종료"""
        if self.frame_reader is not None:
            self.frame_reader.stop()
            self.frame_reader = None
            self.stream_on = False
            self.LOGGER.info("Video stream stopped.")

class FrameReader:
    """비디오 프레임을 백그라운드에서 읽어오는 클래스"""
    def __init__(self, address: str):
        self.address = address
        self.lock = Lock()
        self.frame = None  # 최신 프레임만 유지
        self.stopped = False
        self.worker = Thread(target=self.update_frame, args=(), daemon=True)

    def start(self):
        """프레임 업데이트 시작"""
        self.worker.start()

    def update_frame(self):
        """프레임 업데이트 작업을 수행하는 스레드 함수"""
        try:
            with av.open(self.address, 'r', timeout=(VideoStreamer.FRAME_GRAB_TIMEOUT, None)) as container:
                for frame in container.decode(video=0):
                    # 최신 프레임만 덮어쓰기
                    with self.lock:
                        self.frame = np.array(frame.to_image())

                    if self.stopped:
                        container.close()
                        break
        except av.error.ExitError:
            raise VideoStreamException('Not enough frames for decoding, try again or increase video FPS.')

    @property
    def latest_frame(self):
        """최신 프레임 반환"""
        with self.lock:
            return self.frame

    def stop(self):
        """프레임 수신 스레드 중지"""
        self.stopped = True
