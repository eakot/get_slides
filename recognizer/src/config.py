import os

basedir = os.path.abspath(os.path.dirname(__file__))

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER", "kafka:9092")

KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC = os.getenv("KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC", "download_frame_request")
KAFKA_DOWNLOAD_FRAME_DONE_TOPIC = os.getenv("KAFKA_DOWNLOAD_FRAME_DONE_TOPIC", "download_frame_done")
KAFKA_OCR_FRAME_REQUEST_TOPIC = os.getenv("KAFKA_OCR_FRAME_REQUEST_TOPIC", "ocr_frame_request")
KAFKA_OCR_FRAME_DONE_TOPIC = os.getenv("KAFKA_OCR_FRAME_DONE_TOPIC", "ocr_frame_done")
