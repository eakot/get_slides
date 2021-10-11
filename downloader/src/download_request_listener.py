from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from loguru import logger
import json
import glob
from config import BOOTSTRAP_SERVER, \
    KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC, \
    KAFKA_DOWNLOAD_FRAME_DONE_TOPIC, \
    KAFKA_OCR_FRAME_REQUEST_TOPIC, \
    SAVE_FRAMES_PATH
from pathlib import Path
import os
import subprocess
from shared.kafka_message_models.FramesEvents import DownloadFrameRequest, DownloadFrameDone, OcrFrameRequest


def download(download_frame_request: DownloadFrameRequest):
    video_id = download_frame_request.video_id
    stream_url = download_frame_request.stream_url
    time_sec = download_frame_request.time_sec

    frames_directory = Path(SAVE_FRAMES_PATH).joinpath(video_id)
    Path(frames_directory).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(frames_directory, f"{time_sec}.png")

    load_frame_cmd = f"ffmpeg -y -hide_banner -loglevel error -ss {time_sec} " \
                     f" -i '{stream_url}' -frames:v 1 {filename}"

    logger.debug(f"download {filename}")
    subprocess.check_call(load_frame_cmd, shell=True, stdout=subprocess.PIPE)

    logger.debug(f"Loaded: {filename} ")
    logger.debug(f"Files: {glob.glob(str(frames_directory) + '/*')}")

    return filename


def download_done_message(download_frame_request, filename):
    download_done_message = DownloadFrameDone(
        type="frame_download_request",
        video_id=download_frame_request.video_id,
        frame_id=download_frame_request.frame_id,
        stream_url=download_frame_request.stream_url,
        time_sec=download_frame_request.time_sec,
        filepath=filename)

    download_done_message.event_ts = datetime.now()
    data = download_done_message.json()
    logger.debug("Message {}".format(data))

    return download_done_message


def request_ocr_message(frame_id, filename):
    request_ocr_message = OcrFrameRequest(
        type="frame_ocr_request_from_downloader",
        frame_id=frame_id,
        filename=filename)

    request_ocr_message.event_ts = datetime.now()
    data = request_ocr_message.json()
    logger.debug("Message {}".format(data))

    return request_ocr_message


def download_request_listener(producer: KafkaProducer):
    consumer = KafkaConsumer(KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC,
                             group_id='download_request_listener',
                             bootstrap_servers=BOOTSTRAP_SERVER,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    try:
        for msg in consumer:
            logger.debug(msg)

            download_frame_request: DownloadFrameRequest = DownloadFrameRequest.parse_raw(msg.value)

            filename = download(download_frame_request)

            done_message = download_done_message(download_frame_request, filename)

            producer.send(KAFKA_DOWNLOAD_FRAME_DONE_TOPIC, value=done_message.json())

            ocr_message = request_ocr_message(download_frame_request.frame_id, filename)

            producer.send(KAFKA_OCR_FRAME_REQUEST_TOPIC, value=ocr_message.json())

    finally:
        consumer.close()
