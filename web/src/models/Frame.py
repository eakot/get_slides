import subprocess
from loguru import logger
from timeit import default_timer as timer
from src.models.ocr_utils import ocr_image
from pathlib import Path
# from sqlalchemy.dialects.postgresql import UUID
import os
from src.models.db_object_shared import db
from uuid import uuid3

frames_path = "/data/frames"


class Frame(db.Model):
    __tablename__ = "frame"

    id = db.Column(db.Integer, db.Sequence('frame_id_seq', increment=1), primary_key=True, autoincrement=True)
    filename = db.Column(db.String, primary_key=True)
    video_id = db.Column(db.String, nullable=False)
    stream_url = db.Column(db.String, nullable=False)
    ocr_text = db.Column(db.Text)
    ocr_frame_time_sec = db.Column(db.Float, nullable=True)
    time_sec = db.Column(db.Float, nullable=True)

    def __init__(self, video_id: str, stream_url: str, time_sec: int):
        self.video_id = video_id
        self.stream_url = stream_url
        self.time_sec = time_sec
        frames_directory = Path(frames_path).joinpath(video_id)
        Path(frames_directory).mkdir(parents=True, exist_ok=True)
        self.filename = os.path.join(frames_directory, f"{time_sec}.png")
        self.load_frame_cmd = f"ffmpeg -y -hide_banner -loglevel error -ss {time_sec} " \
                              f" -i '{stream_url}' -frames:v 1 {self.filename}"

        db.session.add(self)
        db.session.commit()
