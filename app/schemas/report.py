from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    avatar: str
    username: str
    created_at: datetime
    scrape_date: datetime
    report_count: int
    score: float
