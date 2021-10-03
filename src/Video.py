from pytube import YouTube
import cv2
import os
import hashlib

import pytesseract

from src.utils import generate_name_from_url, generate_dir


class Video:
    def __init__(self, url):
        self.url = url
        self.filename = generate_name_from_url(url)
        self.download(self.url, self.filename)
        self.frames_filenames = self.save_frames()

    def download(self, url, directory):
        video = YouTube(url).streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution()

        video.download(output_path=directory, filename=self.filename)

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
