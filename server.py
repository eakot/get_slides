from flask import Flask
from flask import render_template, send_file, request, redirect, url_for
from src.utils import *
import pandas as pd

app = Flask(__name__)


@app.route('/get_slides/')
def index():
    return render_template('get_slides/index.html')


@app.route('/get_slides/', methods=['POST', 'GET'])
def index_upload():
    url = request.form['urlInput']
    filename = generate_name_from_url(url)
    load_youtube_video(url, filename)

    frames_filenames = get_frames(filename)

    frames_text_pairs = [[image, ocr_image(image)] for image in frames_filenames]

    frames_text_df = pd.DataFrame(frames_text_pairs, columns=["image", "text"])

    duplicates = remove_duplicates_from_disk(frames_text_df)

    slides = sorted(set(frames_filenames) - set(duplicates))

    frames_text_dict = {i[0]: i[1] for i in frames_text_pairs }
    slides_with_text = {slide: frames_text_dict[slide] for slide in slides}
    return render_template('get_slides/uploaded.html',
                           url=url,
                           filename=filename,
                           frames_text_dict=frames_text_dict,
                           slides_with_text=slides_with_text)



@app.route("/")
def hello_world():
    return "<p>Hello</p>"


@app.route('/.bashrc')
def get_image():
    return send_file(".bashrc", mimetype='text')

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
