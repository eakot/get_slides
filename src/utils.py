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

