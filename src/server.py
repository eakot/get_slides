import pytube
from flask import Flask, url_for, redirect
from flask import render_template, send_file, request
from sqlalchemy import create_engine
from loguru import logger
import json
from src.shared_models import db
from src.models.Video import Video

engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

app = Flask(__name__, template_folder='../templates/', static_folder='../static')
app.config.from_object("src.config.Config")
db.init_app(app)

frames_directory = "static/frames/"


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

    video = Video(frames_directory, video_id)

    db.session.add(video)
    db.session.commit()

    return redirect(url_for('show_slides', video_id=video_id))


@app.route('/get_slides/show/<video_id>', methods=['POST', 'GET'])
def show_slides(video_id):
    video = Video.query.filter_by(video_id=video_id).first()

    if video:
        slides_with_text = json.loads(video.slides_with_text)
        logger.info(f"video found, slides_with_text={slides_with_text}")
        return render_template('get_slides/uploaded.html',
                               slides_with_text=slides_with_text)
    else:
        logger.info(f"requester video not found")
        return redirect(url_for('index',
                                error=f"Send video https://youtu.be/{video_id} to create slides"))


@app.route('/.bashrc')
def get_image():
    return send_file("../.bashrc", mimetype='text')
