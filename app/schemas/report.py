from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    name: str
    username: str
    created_at: datetime
    followers_count: int
    followings_count: int
    scrape_date: datetime
    report_count: int
