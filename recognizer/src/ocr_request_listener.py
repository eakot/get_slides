from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from loguru import logger
import json
import glob
from config import BOOTSTRAP_SERVER, \
    KAFKA_OCR_FRAME_REQUEST_TOPIC, \
    KAFKA_OCR_FRAME_DONE_TOPIC
from shared.kafka_message_models.FramesEvents import OcrFrameRequest, OcrFrameDone
from ocr_utils import ocr_image


def ocr(ocr_frame_request: OcrFrameRequest):
    text = ocr_image(ocr_frame_request.filename)

    return text


def ocr_done_message(ocr_frame_request, text):
    message = OcrFrameDone(
        frame_id=ocr_frame_request.frame_id,
        type="frame_ocr_done",
        filename=ocr_frame_request.filename,
        text=text)

    message.event_ts = datetime.now()
    data = message.json()
    logger.debug("Message {}".format(data))

    return message


def ocr_request_listener(producer):
    consumer = KafkaConsumer(KAFKA_OCR_FRAME_REQUEST_TOPIC,
                             group_id='ocr_request_listener',
                             bootstrap_servers=BOOTSTRAP_SERVER,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    try:
        for msg in consumer:
            logger.debug(msg)

            ocr_frame_request: OcrFrameRequest = OcrFrameRequest.parse_raw(msg.value)

            text = ocr(ocr_frame_request)
            done_message = ocr_done_message(ocr_frame_request, text)
            producer.send(KAFKA_OCR_FRAME_DONE_TOPIC, value=done_message.json())

    finally:
        consumer.close()
