import pytube
from turbo_flask import Turbo
from flask import Flask, url_for, redirect
from flask import render_template, send_file, request
from sqlalchemy import create_engine
from loguru import logger
from src.models.db_object_shared import db
from src.models.Video import Video
import json
from src.config import BOOTSTRAP_SERVER
from kafka import KafkaProducer
import time
import glob

engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

app = Flask(__name__, template_folder='../templates/', static_folder='../static')
app.config.from_object("src.config.Config")
db.init_app(app)
turbo = Turbo(app)

logger.info(f"static folder: {app.static_folder}")
logger.info(f"Frames directory: {glob.glob('../static/data/frames/*')}")


time.sleep(2)
logger.info(f"BOOTSTRAP_SERVER = {BOOTSTRAP_SERVER}")
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVER,
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    api_version=(1, 0, 0)
)


@app.route('/')
def index():
    logger.info("Index requested")
    return render_template('upload.html')


@app.route('/', methods=['POST', 'GET'])
def index_upload():
    url = request.form["urlInput"]
    need_reload_frames = "reloadFrames" in request.form

    video_id = pytube.extract.video_id(url)
    logger.info(f"Add video request, url = {url}, reload_frames={need_reload_frames}")

    video_exists = Video.query.filter_by(video_id=video_id).first()

    if video_exists and need_reload_frames:
        Video.query.filter_by(video_id=video_id).delete()

    if video_exists and not need_reload_frames:
        logger.info(f"Requested video {video_id} already exist in database")
        return redirect(url_for('show_slides', video_id=video_id))

    video = Video(video_id, producer)


    return redirect(url_for('show_slides', video_id=video_id))


@app.route('/search')
def search():
    return render_template('search_slide.html')


@app.route('/show_slides/<video_id>', methods=['POST', 'GET'])
def show_slides(video_id):
    video = Video.query.filter_by(video_id=video_id).first()

    if video:
        slides_with_text = video.get_slides_with_text()
        return render_template('dev/show_slides.html',
                               slides_with_text=slides_with_text)
    else:
        logger.info(f"requested video not found")
        return redirect(url_for('index',
                                error=f"Send video https://youtu.be/{video_id} to create slides"))


@app.route('/.bashrc')
def get_image():
    return send_file("../../.bashrc", mimetype='text')
