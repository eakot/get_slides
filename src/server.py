import pytube
from pytube import YouTube
from flask import Flask, url_for, redirect
from flask import render_template, send_file, request
import pandas as pd
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .get_slides import detect_unique_screenshots, initialize_output_folder
from .utils import *
from loguru import logger
import logging
from sys import stdout
import json

logger.add(stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")


# create a custom handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

app = Flask(__name__, template_folder='../templates/', static_folder='../static')
app.config.from_object("src.config.Config")
app.logger.addHandler(InterceptHandler())
db = SQLAlchemy(app)

video_directory = "static/videos/"


class Video(db.Model):
    __tablename__ = "video"

    video_id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    caption_tracks = db.Column(db.String, nullable=False)
    captions_xml_aen = db.Column(db.Text, nullable=False)
    channel_id = db.Column(db.String, nullable=False)
    channel_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    keywords = db.Column(db.String, nullable=False)
    length_sec = db.Column(db.Integer, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    download_datetime = db.Column(db.Date, nullable=False)
    slides_with_text = db.Column(db.Text)

    def __init__(self, video_id):
        self.directory = video_directory
        self.download_datetime = datetime.now()
        self.url = f"https://youtu.be/{video_id}"
        logger.info(f"url = {self.url}")
        self.video_id = video_id
        logger.info(f"video_id = {self.video_id}")
        self.filename = f"{self.video_id}.mp4"
        logger.info(f"Downloading is being started... out = {self.filename}")
        self.youtube_object = YouTube(self.url)

        self.author = self.youtube_object.author

        self.caption_tracks = str(self.youtube_object.caption_tracks)

        self.captions_xml_aen = self.youtube_object.captions['a.en'].xml_captions

        self.channel_id = self.youtube_object.channel_id
        self.channel_url = self.youtube_object.channel_url
        self.description = self.youtube_object.description
        self.keywords = self.youtube_object.keywords
        self.length_sec = self.youtube_object.length
        self.publish_date = self.youtube_object.publish_date
        self.title = self.youtube_object.title
        self.views = self.youtube_object.views
        self.download_datetime = datetime.now()

        self.download()
        # self.frames_filenames = self.save_unique_frames()
        self.frames_filenames = self.save_frames()

        frames_text_pairs = [[frame, ocr_image(frame)] for frame in self.frames_filenames]

        frames_text_df = pd.DataFrame(frames_text_pairs, columns=["image", "text"])

        # duplicates = remove_duplicates_from_disk(frames_text_df)

        duplicates = remove_duplicates(frames_text_pairs)

        slides = sorted(set(self.frames_filenames) - set(duplicates))
        frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}

        slides_with_text_dict = {slide: frames_text_dict[slide] for slide in slides}

        self.slides_with_text = json.dumps(slides_with_text_dict)

    def download(self):
        video = self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution()

        video.download(output_path=self.directory, filename=self.filename)

        return None

    def save_unique_frames(self):
        video_path = os.path.join(self.directory, self.filename)
        frames_dir = f"static/images/{self.video_id}"
        initialize_output_folder(video_path, frames_dir)
        frames_filenames = detect_unique_screenshots(video_path,
                                                     frames_dir)
        return frames_filenames

    def save_frames(self):
        images_dir = generate_dir(self.filename)
        try:
            os.makedirs(images_dir)
        except OSError:
            print('Error')

        vidcap = cv2.VideoCapture(os.path.join(video_directory, self.filename))
        frames_filenames = []

        def get_frame(sec):
            vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
            hasFrames, image = vidcap.read()
            image_filename = f"{images_dir}/{format(count, '04d')}.jpg"
            if hasFrames:
                frames_filenames.append(image_filename)
                cv2.imwrite(image_filename, image)  # save frame as JPG file
            return hasFrames

        sec = 5
        frame_rate = 10  # //it will capture image in each n second
        count = 1
        success = get_frame(sec)
        while success:
            count = count + 1
            sec = sec + frame_rate
            sec = round(sec, 2)
            success = get_frame(sec)

        return frames_filenames


@logger.catch
@app.route('/get_slides/')
def index():
    logger.info("Index requested")
    return render_template('get_slides/index.html')


@logger.catch
@app.route('/get_slides/', methods=['POST', 'GET'])
def index_upload():
    url = request.form['urlInput']
    video_id = pytube.extract.video_id(url)
    logger.info(f"Add video request, url = {url}")

    video_exists = Video.query.filter_by(video_id=video_id).first()

    if video_exists:
        logger.info(f"Requested video {video_id} already exist in database")
        return redirect(url_for('show_slides', video_id=video_id))

    else:
        video = Video(video_id)

        db.session.add(video)
        db.session.commit()

        slides_with_text = json.loads(video.slides_with_text)
        return render_template('get_slides/uploaded.html',
                               slides_with_text=slides_with_text)


@logger.catch
@app.route('/get_slides/show/<video_id>', methods=['POST', 'GET'])
def show_slides(video_id):
    video = Video.query.filter_by(video_id=video_id).first()

    if video:
        return render_template('get_slides/uploaded.html',
                               slides_with_text=json.loads(video.slides_with_text))
    else:
        return redirect(url_for('index',
                                error=f"Send video https://youtu.be/{video_id} to create slides"))


@app.route("/")
def hello_world():
    return "<p>Hello</p>"


@app.route('/.bashrc')
def get_image():
    return send_file("../.bashrc", mimetype='text')

# import os
# from http.server import HTTPServer, CGIHTTPRequestHandler
#
# # Make sure the server is created at current directory
# os.chdir('.')
#
# # Create server object listening the port 80
# server_object = HTTPServer(server_address=('', 80), RequestHandlerClass=CGIHTTPRequestHandler)
#
# # Start the web server
# server_object.serve_forever()
