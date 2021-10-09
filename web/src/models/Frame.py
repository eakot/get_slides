import shutil
import subprocess
from loguru import logger

from src.models.ocr_utils import ocr_image
from src.models.shared import db
from pathlib import Path


class Frame(db.Model):
    __tablename__ = "frame"

    filename = db.Column(db.String, primary_key=True)
    video_id = db.Column(db.String, nullable=False)
    stream_url = db.Column(db.String, nullable=False)
    ocr_text = db.Column(db.Text)
    time_sec = db.Column(db.Float, nullable=False)

    def __init__(self, frames_path: str, stream_url: str, time_sec):
        self.stream_url = stream_url
        self.time_sec = time_sec
        self.filename = f"{str(frames_path)}/{time_sec}.png"
        self.load_frame_cmd = f"ffmpeg -hide_banner -loglevel error -ss {time_sec} " \
                              f" -i '{stream_url}' -frames:v 1 {self.filename}"

    def download(self):
        status = subprocess.Popen(self.load_frame_cmd, shell=True)
        status.wait()
        return self.filename

    def recognize_text(self):
        self.ocr_text = ocr_image(self.filename)
        return self.ocr_text

    @staticmethod
    def prepare_directory(frames_directory: str):
        frames_path = Path(frames_directory)
        logger.info(f"frames_path = {frames_path}")
        frames_path.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(frames_path, ignore_errors=False)
        frames_path.mkdir(parents=True, exist_ok=True)

        return frames_path

    @staticmethod
    def download_frames(frames):
        for frame in frames:
            status = subprocess.Popen(frame.load_frame_cmd, shell=True)
            status.wait()

        return [f.frame_filename for f in frames]
