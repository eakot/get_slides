import shutil

import pytube
from pytube import YouTube
from flask import Flask, url_for, redirect
from flask import render_template, send_file, request
import pandas as pd
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import subprocess
from .utils import *
from loguru import logger
import logging
from sys import stdout
import json
from pathlib import Path
from timeit import default_timer as timer

# logger.add(stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")


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

frames_directory = "static/frames/"


class Video(db.Model):
    __tablename__ = "video"

    video_id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    stream_url = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    caption_tracks = db.Column(db.String, nullable=False)
    captions_xml_aen = db.Column(db.Text, nullable=False)
    channel_id = db.Column(db.String, nullable=False)
    channel_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    keywords = db.Column(db.String, nullable=False)
    length_sec = db.Column(db.Integer, nullable=False)
    download_frames_time_sec = db.Column(db.Float, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    download_datetime = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    frames_directory = db.Column(db.Text, nullable=False)
    slides_with_text = db.Column(db.Text)

    def __init__(self, video_id):
        self.download_datetime = datetime.now()
        self.url = f"https://youtu.be/{video_id}"
        logger.info(f"url = {self.url}")
        self.video_id = video_id
        logger.info(f"video_id = {self.video_id}")
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
        self.frames_directory = os.path.join(frames_directory, self.video_id)

        self.stream_url = self.get_stream_url()
        # self.frames_filenames = self.save_unique_frames()
        logger.info(f"Download started ")
        download_start_time = timer()
        self.frames_filenames = self.download_frames()
        download_end_time = timer()
        self.download_frames_time_sec = download_end_time - download_start_time
        logger.info(f"Download finished in {self.download_frames_time_sec } sec")

        frames_text_pairs = [[frame, ocr_image(frame)] for frame in self.frames_filenames]

        duplicates = remove_duplicates_or_empty(frames_text_pairs)

        slides = sorted(set(self.frames_filenames) - set(duplicates))
        frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}

        slides_with_text_dict = {slide: frames_text_dict[slide] for slide in slides}

        self.slides_with_text = json.dumps(slides_with_text_dict)

    def get_stream_url(self):
        return self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution().url

    def download_frames(self):

        frame_rate = 10  # get frame every 'frame_rate'seconds
        subprocesses_parallelism = 2  # number of parallel subprocesses with ffmpeg request
        ffmpeg_request_sequence_len = 10  # number of ffmpeg runs in each subprocess

        frames_path = Path(self.frames_directory)
        frames_path.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(self.frames_directory, ignore_errors=False)
        frames_path.mkdir(parents=True, exist_ok=True)
        child_processes = []
        ffmpeg_request_sequence = []

        for sec in range(0, self.length_sec, frame_rate):
            load_frame_cmd = f"ffmpeg -hide_banner -loglevel error -ss {sec} -i '{self.stream_url}' -frames:v 1 {self.frames_directory}/{sec}.png"
            ffmpeg_request_sequence.append(load_frame_cmd)

            if len(ffmpeg_request_sequence) % ffmpeg_request_sequence_len == 0:
                subprocess_call_str = " && ".join(ffmpeg_request_sequence)
                logger.info(f"{sec}/{self.length_sec}: subprocess_call_str: {len(ffmpeg_request_sequence)} ffmpeg runs")
                status = subprocess.Popen(subprocess_call_str, shell=True)
                child_processes.append(status)

                ffmpeg_request_sequence = []

            if len(child_processes) % subprocesses_parallelism == 0:
                logger.info(f"{sec}/{self.length_sec}: subprocesses_parallelism: exec process.wait()")
                for p in child_processes:
                    p.wait()

                child_processes = []

        frames_filenames = [str(p) for p in frames_path.iterdir()]

        return frames_filenames


@app.route('/get_slides/')
def index():
    logger.info("Index requested")
    return render_template('get_slides/index.html')


@app.route('/get_slides/', methods=['POST', 'GET'])
def index_upload():
    url = request.form["urlInput"]
    reload_frames = "reloadFrames" in request.form

    video_id = pytube.extract.video_id(url)
    logger.info(f"Add video request, url = {url}, reload_frames={reload_frames}")

    video_exists = Video.query.filter_by(video_id=video_id).first()

    if video_exists and reload_frames:
        Video.query.filter_by(video_id=video_id).delete()

    if video_exists and not reload_frames:
        logger.info(f"Requested video {video_id} already exist in database")
        return redirect(url_for('show_slides', video_id=video_id))

    video = Video(video_id)

    db.session.add(video)
    db.session.commit()

    # slides_with_text = json.loads(video.slides_with_text)
    return redirect(url_for('show_slides', video_id=video_id))


@app.route('/get_slides/show/<video_id>', methods=['POST', 'GET'])
def show_slides(video_id):
    video = Video.query.filter_by(video_id=video_id).first()

    if video:
        return render_template('get_slides/uploaded.html',
                               slides_with_text=json.loads(video.slides_with_text))
    else:
        return redirect(url_for('index',
                                error=f"Send video https://youtu.be/{video_id} to create slides"))


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
