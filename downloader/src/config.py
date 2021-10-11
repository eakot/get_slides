import os

basedir = os.path.abspath(os.path.dirname(__file__))

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER", "kafka:9092")


KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC = os.getenv("KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC", "download_frame_request")
KAFKA_DOWNLOAD_FRAME_DONE_TOPIC = os.getenv("KAFKA_DOWNLOAD_FRAME_DONE_TOPIC", "download_frame_done")
KAFKA_OCR_FRAME_REQUEST_TOPIC = os.getenv("KAFKA_OCR_FRAME_REQUEST_TOPIC", "ocr_frame_request")

SAVE_FRAMES_PATH = os.getenv("SAVE_FRAMES_PATH", "/data/frames")
FRAME_RATE_DOWNLOAD = os.getenv("FRAME_RATE_DOWNLOAD", 10)


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_APP = os.getenv("FLASK_APP", "../__init__.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
