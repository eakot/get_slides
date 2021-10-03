from pytube import YouTube
import cv2
import os
import hashlib
import pytesseract
from datetime import datetime
from src.utils import generate_name_from_url, generate_dir
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import insert

Base = declarative_base()


class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    filename = Column(String)
    title = Column(String)

    def __init__(self, engine, url, video_directory):
        self.directory = video_directory

        self.url = url
        self.filename = generate_name_from_url(url)

        youtube_object = YouTube(self.url)

        self.youtube_info = self.get_video_info(youtube_object)

        with engine.connect() as conn:
            result = conn.execute(
                insert(self.__tablename__),
                [{"id": 1,
                  "url": self.url,
                  "filename": self.filename,
                  "title": self.title},
                 ]
            )
            conn.commit()

        self.download(youtube_object)
        self.frames_filenames = self.save_frames(video_directory)

    def download(self, youtube_object):
        video = youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution()

        video.download(output_path=self.directory, filename=self.filename)

        return video

    def save_frames(self, video_directory):
        images_dir = generate_dir(self.filename)
        try:
            os.makedirs(images_dir)
        except OSError:
            print('Error')

        vidcap = cv2.VideoCapture(os.path.join(video_directory, self.filename))
        images_filenames = []

        def get_frame(sec):
            vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
            hasFrames, image = vidcap.read()
            image_filename = f"{images_dir}/{format(count, '04d')}.jpg"
            if hasFrames:
                images_filenames.append(image_filename)
                cv2.imwrite(image_filename, image)  # save frame as JPG file
            return hasFrames

        sec = 0
        frame_rate = 10  # //it will capture image in each n second
        count = 1
        success = get_frame(sec)
        while success:
            count = count + 1
            sec = sec + frame_rate
            sec = round(sec, 2)
            success = get_frame(sec)

        return images_filenames

    def get_video_info(self, youtube_object):
        info = {
            "author": youtube_object.author,
            "caption_tracks": youtube_object.caption_tracks,
            "captions": youtube_object.captions,
            "channel_id": youtube_object.channel_id,
            "channel_url": youtube_object.channel_url,
            "description": youtube_object.description,
            "keywords": youtube_object.keywords,
            "length_sec": youtube_object.length,
            "publish_date": youtube_object.publish_date,
            "title": youtube_object.title,
            "views": youtube_object.views,
            "download_datetime": datetime.now()
        }

        return info
