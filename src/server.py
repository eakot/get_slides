from flask import Flask
from flask import render_template, send_file, request
import pandas as pd
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from pytube import YouTube
from datetime import datetime
import cv2
import os
from .utils import *

engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

app = Flask(__name__, template_folder='../templates/', static_folder='../static')
app.config.from_object("src.config.Config")

db = SQLAlchemy(app)

video_directory = "static/videos/"


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    # filename = db.Column(String, unique=True, nullable=False)
    title = db.Column(db.String)

    def __init__(self, engine, url, video_directory):
        self.directory = video_directory

        self.url = url
        self.filename = generate_name_from_url(url)

        self.youtube_object = YouTube(self.url)

        self.youtube_info = self.get_video_info(self.youtube_object)

        self.download()
        self.frames_filenames = self.save_frames()

    def download(self):
        video = self.youtube_object.streams \
            .filter(file_extension='mp4') \
            .get_highest_resolution()

        video.download(output_path=self.directory, filename=self.filename)

        return None

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

        sec = 0
        frame_rate = 10  # //it will capture image in each n second
        count = 1
        success = get_frame(sec)
        while success:
            count = count + 1
            sec = sec + frame_rate
            sec = round(sec, 2)
            success = get_frame(sec)

        return frames_filenames

    def get_video_info(self, youtube_object):
        info = {
            "author": youtube_object.author,
            "caption_tracks": youtube_object.caption_tracks,
            "captions": youtube_object.captions,
            "channel_id": youtube_object.channel_id,
            "channel_url": youtube_object.channel_url,
            "description": youtube_object.description,
            "keywords": youtube_object.keywords,
            "length_sec": youtube_object.length,
            "publish_date": youtube_object.publish_date,
            "title": youtube_object.title,
            "views": youtube_object.views,
            "download_datetime": datetime.now()
        }

        return info


@app.route('/get_slides/')
def index():
    return render_template('get_slides/index.html')


@app.route('/get_slides/', methods=['POST', 'GET'])
def index_upload():
    url = request.form['urlInput']
    video = Video(engine, url, video_directory)

    db.session.add(video)
    db.session.commit()

    frames_text_pairs = [[frame, ocr_image(frame)] for frame in video.frames_filenames]

    frames_text_df = pd.DataFrame(frames_text_pairs, columns=["image", "text"])

    duplicates = remove_duplicates_from_disk(frames_text_df)

    slides = sorted(set(video.frames_filenames) - set(duplicates))

    frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}
    slides_with_text = {slide: frames_text_dict[slide] for slide in slides}
    return render_template('get_slides/uploaded.html',
                           url=video.url,
                           filename=video.filename,
                           youtube_info=video.youtube_info,
                           frames_text_dict=frames_text_dict,
                           slides_with_text=slides_with_text)


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
