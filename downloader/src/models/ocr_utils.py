import re

import cv2
import os
import numpy as np
import pytesseract
import fire
from loguru import logger
from difflib import SequenceMatcher

try:
    from PIL import Image
except ImportError:
    import Image


def clear_text(t: str) -> str:
    regex = re.compile('[^a-zA-Zа-яА-ЯеЁ]')
    t = regex.sub(' ', t)
    words = sorted(t.lower().split())
    return ' '.join(w for w in words if len(w) > 4)


def similar(a, b):
    clear_a = clear_text(a)
    clear_b = clear_text(b)
    logger.debug(f"clear_a: {clear_a}")
    logger.debug(f"clear_b: {clear_b}")
    sim = SequenceMatcher(None, clear_a, clear_b).ratio()
    logger.debug(f"sim: {sim}")
    return sim


def remove_duplicates_or_empty(frames_text_list):
    to_delete = []

    if len(frames_text_list) > 0:
        regex = re.compile('[\s+]')
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


def ocr_image(filename):
    logger.info(f"ocr_image( {filename} )")
    image = cv2.imread(filename)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    # image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    # image = cv2.Canny(image, 100, 200)

    text = pytesseract \
        .image_to_string(image, lang='eng', config='--psm 4')

    text = "\n".join([ll.rstrip() for ll in text.splitlines() if ll.strip()])

    text = re.compile(r"[^a-zA-Z0-9-\n]+").sub(" ", text)

    return text


if __name__ == '__main__':
    fire.Fire()
