from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class NewVideoEvent(BaseModel):
    type: str
    video_id: str
    stream_url: str
    event_ts: Optional[datetime] = None
