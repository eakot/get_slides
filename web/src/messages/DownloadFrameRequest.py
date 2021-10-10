from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class DownloadFrameRequest(BaseModel):
    type: str
    video_id: str
    stream_url: str
    time_sec: int
    event_ts: Optional[datetime] = None