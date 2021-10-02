from pytube import YouTube
import cv2
import os
import hashlib

import pytesseract

try:
    from PIL import Image
except ImportError:
    import Image


def remove_duplicates_from_disk(frames_text_df):
    duplicates = frames_text_df["image"][frames_text_df.duplicated("text")] \
        .to_list()
    for duplicated_frame in duplicates:
        os.remove(duplicated_frame)
        
    return duplicates


def ocr_image(filename):
    return pytesseract \
        .image_to_string(Image.open(filename),
                         lang='eng+rus')


def generate_name_from_url(url):
    return hashlib.sha1(url.encode('utf-8')).hexdigest() + ".mp4"


def generate_dir(filename):
    return f'static/images/{"_".join(filename.split(".")[:-1])}'


def load_youtube_video(url, filename):
    video = YouTube(url).streams \
        .filter(file_extension='mp4') \
        .get_highest_resolution()

    video.download(output_path="./tmp/", filename=filename)

    return video


def get_frames(filename):
    images_dir = generate_dir(filename)
    try:
        os.makedirs(images_dir)
    except OSError:
        print('Error')

    vidcap = cv2.VideoCapture(f'tmp/{filename}')
    images_filenames = []

    def get_frame(sec):
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        hasFrames, image = vidcap.read()
        image_filename = f"{images_dir}/{format(count, '03d')}.jpg"
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
