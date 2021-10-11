import fire
from kafka import KafkaProducer
import json
from ocr_request_listener import ocr_request_listener
from loguru import logger

from config import BOOTSTRAP_SERVER


def run_listeners():
    logger.info("run consumer")

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        api_version=(1, 0, 0)
    )
    ocr_request_listener(producer)


if __name__ == '__main__':
    fire.Fire(run_listeners)
