import fire
from consumer import run_listener
from loguru import logger

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def consumer(bootstrap_server="kafka:9092", topic="frames"):
    logger.info("run consumer")

    # https://stackoverflow.com/a/55070154/7997244

    engine = create_engine('postgresql://postgres:postgres@db:5432/postgres', echo=True)
    Base = declarative_base()
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()

    run_listener(session, bootstrap_server, topic)


if __name__ == '__main__':
    fire.Fire(consumer)
