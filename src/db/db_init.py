from sqlalchemy import MetaData

from sqlalchemy import Table, Column, Integer, String

metadata_obj = MetaData()

video_table = Table(
    "video",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('url', String),
    Column('title', String)
)


def create_all(engine):
    metadata_obj.create_all(engine)
    return None
