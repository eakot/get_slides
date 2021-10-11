from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class DownloadFrameRequest(BaseModel):
    type: str
    video_id: str
    frame_id: int
    stream_url: str
    time_sec: int
    event_ts: Optional[datetime] = None


class DownloadFrameDone(BaseModel):
    type: str
    video_id: str
    frame_id: int
    stream_url: str
    time_sec: int
    filepath: str
    event_ts: Optional[datetime] = None


class OcrFrameRequest(BaseModel):
    frame_id: int
    type: str
    filename: str
    event_ts: Optional[datetime] = None


class OcrFrameDone(BaseModel):
    frame_id: int
    type: str
    filename: str
    text: str
    event_ts: Optional[datetime] = None
