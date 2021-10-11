import datetime
import re
import os
import uuid
from datetime import datetime
from loguru import logger
from difflib import SequenceMatcher
from pytube import YouTube
from sqlalchemy.dialects.postgresql import UUID

from src.shared.kafka_message_models.FramesEvents import DownloadFrameRequest
from src.shared.kafka_message_models.VideosEvents import NewVideoEvent
from src.models.Frame import Frame
from src.models.db_object_shared import db
from src.config import FRAME_RATE_DOWNLOAD, KAFKA_VIDEOS_TOPIC, KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    stream_url = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    caption_tracks = db.Column(db.String, nullable=False)
    captions_xml_aen = db.Column(db.Text, nullable=True)
    channel_id = db.Column(db.String, nullable=False)
    channel_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    keywords = db.Column(db.String, nullable=False)
    length_sec = db.Column(db.Integer, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    add_datetime = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, nullable=False)

    def __init__(self, video_id, producer):
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
        self.add_datetime = datetime.now()

        self.stream_url = self.get_stream_url()
        self.send_new_video_event(producer)

        frames = self.create_frames()
        Video.request_download(frames, producer)

        db.session.add(self)
        db.session.commit()
        # Video.ocr_frames(frames)

        # self.frames_filenames = [f.filename for f in frames]
        #
        # frames_text_pairs = [[f.filename, f.ocr_text] for f in frames]
        #
        # duplicates = Frame.remove_duplicates_or_empty(frames_text_pairs)
        #
        # slides = sorted(set(self.frames_filenames) - set(duplicates))
        # frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}
        #
        # slides_with_text_dict = {slide: frames_text_dict[slide] for slide in slides}
        #
        # self.slides_with_text = json.dumps(slides_with_text_dict)

    def get_stream_url(self):
        return self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution().url

    def send_new_video_event(self, producer):
        new_event = NewVideoEvent(
            type="new_video_from_user",
            video_id=self.video_id,
            stream_url=self.stream_url)

        new_event.event_ts = datetime.now()
        data = new_event.json()
        logger.debug("Message {}".format(data))
        producer.send(KAFKA_VIDEOS_TOPIC, value=data)

        return None

    def create_frames(self):
        frames = []
        for sec in range(10, self.length_sec, FRAME_RATE_DOWNLOAD):
            frames.append(Frame(video_id=self.video_id,
                                stream_url=self.stream_url,
                                time_sec=sec)
                          )

        return frames

    @staticmethod
    def request_download(frames, producer):
        for frame in frames:
            new_event = DownloadFrameRequest(
                type="frame_download_request_from_web",
                video_id=frame.video_id,
                frame_id=frame.id,
                stream_url=frame.stream_url,
                time_sec=frame.time_sec)

            new_event.event_ts = datetime.now()
            data = new_event.json()
            logger.debug("Message {}".format(data))
            producer.send(KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC, value=data)

        return None
    #
    # @staticmethod
    # def ocr_frames(frames):
    #     for frame in frames:
    #         frame.ocr_frame()
    #     return None

    @staticmethod
    def remove_duplicates_or_empty(frames_text_list):

        def similar(a, b):
            def clear_text(t: str) -> str:
                alphabet_only_regex = re.compile('[^a-zA-Zа-яА-ЯеЁ]')
                t = alphabet_only_regex.sub(' ', t)
                words = sorted(t.lower().split())
                return ' '.join(w for w in words if len(w) > 4)

            clear_a = clear_text(a)
            clear_b = clear_text(b)
            logger.debug(f"clear_a: {clear_a}")
            logger.debug(f"clear_b: {clear_b}")
            is_sim = SequenceMatcher(None, clear_a, clear_b).ratio()
            logger.debug(f"sim: {is_sim}")
            return is_sim

        to_delete = []

        if len(frames_text_list) > 0:
            regex = re.compile('[/s+]')
            text_prev = frames_text_list[0][1]
            if len(regex.sub('', text_prev)) == 0:
                to_delete.append(frames_text_list[0][0])

            for i in range(1, len(frames_text_list)):
                image = frames_text_list[i][0]
                text = frames_text_list[i][1]

                if len(regex.sub('', text)) == 0:
                    to_delete.append(image)
                else:
                    sim = similar(text_prev, text)
                    logger.info(f"i = {i}, sim = {sim}")
                    if sim > 0.8:
                        to_delete.append(image)
                    else:
                        text_prev = text

            logger.info(f"duplicates: {to_delete}")
            for f in to_delete:
                os.remove(f)

        return to_delete

    def get_slides_with_text(self):
        frames = Frame.query.filter_by(video_id=self.video_id).all()
        frame_text_dict = {'../static/' + f.filename: f.ocr_text for f in frames}
        logger.debug(f"frames found: {frame_text_dict.keys()}")
        return frame_text_dict
