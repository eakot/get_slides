import re

import cv2
import os
import numpy as np
import pytesseract
import fire
from loguru import logger
try:
    from PIL import Image
except ImportError:
    import Image

from difflib import SequenceMatcher


def images_ocr_similar(a, b):
    text_a = ocr_image(a)
    text_b = ocr_image(b)

    print(text_a)
    print(text_b)
    return similar(a, b)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def remove_duplicates(frames_text_list):
    duplicates = []
    text_prev = frames_text_list[0][1]
    for i in range(1, len(frames_text_list)):
        image = frames_text_list[i][0]
        text = frames_text_list[i][1]
        sim = similar(text_prev, text)
        logger.info(f"i = {i}, sim = {sim}")
        if sim > 0.8:
            duplicates.append(image)
        else:
            text_prev = text

    logger.info(f"duplicates: {duplicates}")
    for duplicated_frame in duplicates:
        os.remove(duplicated_frame)

    return duplicates


def remove_duplicates_from_disk(frames_text_df):
    duplicates = frames_text_df["image"][frames_text_df.duplicated("text")] \
        .to_list()

    for duplicated_frame in duplicates:
        os.remove(duplicated_frame)

    return duplicates


def ocr_image(filename):
    image = cv2.imread(filename)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    # image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    # image = cv2.Canny(image, 100, 200)

    text = pytesseract \
        .image_to_string(image, lang='eng')

    text = "\n".join([ll.rstrip() for ll in text.splitlines() if ll.strip()])

    text = re.compile(r"[^a-zA-Z0-9-\n]+").sub(" ", text)

    return text


def generate_name_from_url(url):
    return


def generate_dir(filename):
    return f'static/images/{"_".join(filename.split(".")[:-1])}'


if __name__ == '__main__':
    fire.Fire()
