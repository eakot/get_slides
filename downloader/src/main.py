import json

import fire
from kafka import KafkaProducer

from download_request_listener import download_request_listener
from loguru import logger
from config import BOOTSTRAP_SERVER


def run_listeners():
    logger.info("run consumer")

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        api_version=(1, 0, 0)
    )

    download_request_listener(producer)


if __name__ == '__main__':
    fire.Fire(run_listeners)
