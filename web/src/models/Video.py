import datetime
import glob

from pytube import YouTube
from src.models.shared import db
from datetime import datetime
from loguru import logger

from src.config import FRAME_RATE_DOWNLOAD, KAFKA_FRAMES_DOWNLOAD_TOPIC
from src.messages.DownloadFrameRequest import DownloadFrameRequest


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
    publish_date = db.Column(db.Date, nullable=False)
    download_datetime = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, nullable=False)

    def __init__(self, frames_directory, video_id, producer):
        self.download_datetime = datetime.now()
        self.url = f"https://youtu.be/{video_id}"
        logger.info(f"url = {self.url}")
        self.video_id = video_id
        logger.info(f"video_id = {self.video_id}")
        self.youtube_object = YouTube(self.url)

        self.author = self.youtube_object.author

        self.caption_tracks = str(self.youtube_object.caption_tracks)

        self.captions_xml_aen = ""  # self.youtube_object.captions['a.en'].xml_captions

        self.channel_id = self.youtube_object.channel_id
        self.channel_url = self.youtube_object.channel_url
        self.description = self.youtube_object.description
        self.keywords = self.youtube_object.keywords
        self.length_sec = self.youtube_object.length
        self.publish_date = self.youtube_object.publish_date
        self.title = self.youtube_object.title
        self.views = self.youtube_object.views
        self.download_datetime = datetime.now()

        self.stream_url = self.get_stream_url()

        self.download_frames(producer)

    def get_stream_url(self):
        return self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution().url

    def download_frames(self, producer):
        logger.info(f"Download started ")

        for sec in range(10, self.length_sec, FRAME_RATE_DOWNLOAD):
            new_event = DownloadFrameRequest(
                type="frame_download_request",
                video_id=self.video_id,
                stream_url=self.stream_url, time_sec=sec)

            new_event.event_ts = datetime.now()
            data = new_event.json()
            logger.debug("Message {}".format(data))
            producer.send(KAFKA_FRAMES_DOWNLOAD_TOPIC, value=data)

        return None

    def get_slides(self):
        files = glob.glob(f'static/frames/{self.video_id}/*')
        logger.debug(f"files in {f'/data/frames/{self.video_id}/*'} found: {files}")
        return files
