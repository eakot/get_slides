import shutil
import subprocess
from loguru import logger

from timeit import default_timer as timer
from models.ocr_utils import ocr_image
from pathlib import Path
from sqlalchemy import Column, Text, String, Float
import os

frames_path = "/data/frames"


class Frame():
    __tablename__ = "frame"

    filename = Column(String, primary_key=True)
    video_id = Column(String, nullable=False)
    stream_url = Column(String, nullable=False)
    ocr_text = Column(Text)
    ocr_frame_time_sec = Column(Float, nullable=False)
    time_sec = Column(Float, nullable=False)

    def __init__(self, video_id: str, stream_url: str, time_sec: int):
        self.stream_url = stream_url
        self.time_sec = time_sec
        frames_directory = Path(frames_path).joinpath(video_id)
        Path(frames_directory).mkdir(parents=True, exist_ok=True)
        self.filename = os.path.join(frames_directory, f"{time_sec}.png")
        self.load_frame_cmd = f"ffmpeg -y -hide_banner -loglevel error -ss {time_sec} " \
                              f" -i '{stream_url}' -frames:v 1 {self.filename}"

    def download(self):
        logger.debug(f"download {self.filename}")
        subprocess.check_call(self.load_frame_cmd, shell=True, stdout=subprocess.PIPE)
        return self.filename

    def ocr_frame(self):
        logger.info(f"OCR started ")
        ocr_start_time = timer()
        self.ocr_text = ocr_image(self.filename)
        ocr_end_time = timer()
        ocr_frames_time_sec = ocr_end_time - ocr_start_time
        logger.info(f"OCR finished in {ocr_frames_time_sec} sec")

        self.ocr_frame_time_sec

        return None
