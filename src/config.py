import os

basedir = os.path.abspath(os.path.dirname(__file__))
FRAME_RATE_DOWNLOAD = 10  # get frame every 'frame_rate'seconds


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_APP = os.getenv("FLASK_APP", "__init__.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
