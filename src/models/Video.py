import datetime
import json
from pytube import YouTube
from timeit import default_timer as timer
from datetime import datetime
from src.models.ocr_utils import *
from src.models.Frame import Frame
from src.shared_models import db

from src.config import FRAME_RATE_DOWNLOAD


class Video(db.Model):
    __tablename__ = "video"

    video_id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    stream_url = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    caption_tracks = db.Column(db.String, nullable=False)
    captions_xml_aen = db.Column(db.Text, nullable=False)
    channel_id = db.Column(db.String, nullable=False)
    channel_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    keywords = db.Column(db.String, nullable=False)
    length_sec = db.Column(db.Integer, nullable=False)
    download_frames_time_sec = db.Column(db.Float, nullable=False)
    ocr_frames_time_sec = db.Column(db.Float, nullable=True)
    publish_date = db.Column(db.Date, nullable=False)
    download_datetime = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    frames_directory = db.Column(db.Text, nullable=False)
    slides_with_text = db.Column(db.Text)

    def __init__(self, frames_directory, video_id):
        self.download_datetime = datetime.now()
        self.url = f"https://youtu.be/{video_id}"
        logger.info(f"url = {self.url}")
        self.video_id = video_id
        logger.info(f"video_id = {self.video_id}")
        self.youtube_object = YouTube(self.url)

        self.author = self.youtube_object.author

        self.caption_tracks = str(self.youtube_object.caption_tracks)

        self.captions_xml_aen = self.youtube_object.captions['a.en'].xml_captions

        self.channel_id = self.youtube_object.channel_id
        self.channel_url = self.youtube_object.channel_url
        self.description = self.youtube_object.description
        self.keywords = self.youtube_object.keywords
        self.length_sec = self.youtube_object.length
        self.publish_date = self.youtube_object.publish_date
        self.title = self.youtube_object.title
        self.views = self.youtube_object.views
        self.download_datetime = datetime.now()
        self.frames_directory = os.path.join(frames_directory, self.video_id)

        self.stream_url = self.get_stream_url()

        frames = self.create_frames()

        self.download_frames_time_sec = Video.download_frames(frames)

        self.ocr_frames_time_sec = Video.ocr_frames(frames)

        self.frames_filenames = [f.filename for f in frames]

        frames_text_pairs = [[f.filename, f.ocr_text] for f in frames]

        duplicates = remove_duplicates_or_empty(frames_text_pairs)

        slides = sorted(set(self.frames_filenames) - set(duplicates))
        frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}

        slides_with_text_dict = {slide: frames_text_dict[slide] for slide in slides}

        self.slides_with_text = json.dumps(slides_with_text_dict)

    def get_stream_url(self):
        return self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution().url

    def create_frames(self):
        frames_path = Frame.prepare_directory(self.frames_directory)
        frames = []
        for sec in range(10, self.length_sec, FRAME_RATE_DOWNLOAD):
            frames.append(Frame(frames_path=frames_path,
                                stream_url=self.stream_url,
                                time_sec=sec
                                ))
        return frames

    @staticmethod
    def ocr_frames(frames):
        logger.info(f"OCR started ")
        ocr_start_time = timer()
        [f.recognize_text() for f in frames]
        ocr_end_time = timer()
        ocr_frames_time_sec = ocr_end_time - ocr_start_time
        logger.info(f"OCR finished in {ocr_frames_time_sec} sec")
        return ocr_frames_time_sec

    @staticmethod
    def download_frames(frames):
        logger.info(f"Download started ")
        download_start_time = timer()
        [f.download() for f in frames]
        download_end_time = timer()
        download_frames_time_sec = download_end_time - download_start_time
        logger.info(f"Download finished in {download_frames_time_sec} sec")
        return download_frames_time_sec

