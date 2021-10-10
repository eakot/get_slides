from pathlib import Path

from kafka import KafkaConsumer
from loguru import logger
from models.Frame import Frame
from messages.DownloadFrameRequest import DownloadFrameRequest
import json
import glob


def run_listener(session, bootstrap_server, topic):
    consumer = KafkaConsumer(topic,
                             group_id='downloader',
                             bootstrap_servers=bootstrap_server,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    for msg in consumer:
        logger.debug(msg)

        logger.debug(f" message value: {msg.value}")
        parsed = DownloadFrameRequest.parse_raw(msg.value)
        logger.debug(f"Parsed message: {parsed}")

        frame = Frame(video_id=parsed.video_id,
                      stream_url=parsed.stream_url,
                      time_sec=parsed.time_sec)
        #
        filename = frame.download()
        logger.debug(f"Loaded: {filename} ")
        logger.debug(f"Files: {glob.glob('/data/frames/y6gTsj6okHE/*')}")

        # frame.ocr_frame()

        # logger.debug(f"ocr_text: {frame.ocr_text}")
        #
        # self.frames_filenames = [f.filename for f in frames]
        #
        # frames_text_pairs = [[f.filename, f.ocr_text] for f in frames]
        #
        # duplicates = remove_duplicates_or_empty(frames_text_pairs)
        #
        # slides = sorted(set(self.frames_filenames) - set(duplicates))
        # frames_text_dict = {i[0]: i[1] for i in frames_text_pairs}
        #
        # slides_with_text_dict = {slide: frames_text_dict[slide] for slide in slides}
        #
        # self.slides_with_text = json.dumps(slides_with_text_dict)
