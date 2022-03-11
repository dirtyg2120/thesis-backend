from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.tweet import Tweet


class ReportResponse(BaseModel):
    id: str
    name: str
    username: str
    created_at: datetime
    followers_count: int
    followings_count: int
    scrape_date: datetime
    reset_date: datetime
    report_count: int
