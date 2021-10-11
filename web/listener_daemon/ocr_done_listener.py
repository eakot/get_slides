from flask import Flask
from sqlalchemy import create_engine
from kafka import KafkaConsumer
from loguru import logger
import json
from src.config import BOOTSTRAP_SERVER, \
    KAFKA_OCR_FRAME_DONE_TOPIC
from src.shared.kafka_message_models.FramesEvents import OcrFrameDone
from src.models.Frame import Frame
from src.models.db_object_shared import db

engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

app = Flask(__name__)
app.config.from_object("src.config.Config")
db.init_app(app)
consumer = KafkaConsumer(KAFKA_OCR_FRAME_DONE_TOPIC,
                         group_id='web_ocr_done_listener',
                         bootstrap_servers=BOOTSTRAP_SERVER,
                         api_version=(1, 0, 0),
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

with app.app_context():
    try:
        for msg in consumer:
            logger.debug(msg)

            ocr_frame_done: OcrFrameDone = OcrFrameDone.parse_raw(msg.value)

            text = ocr_frame_done.text
            frame = Frame.query.filter_by(id=ocr_frame_done.frame_id).first()
            frame.ocr_text = text
            db.session.commit()

    finally:
        consumer.close()


