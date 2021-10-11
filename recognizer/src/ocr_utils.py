import re
import cv2
import numpy as np
import pytesseract
import fire
from loguru import logger

try:
    from PIL import Image
except ImportError:
    import Image


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
