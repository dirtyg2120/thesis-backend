from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    avatar: str
    username: str
    created_at: datetime
    scrape_date: datetime
    report_count: int
    score: float


class ReportProcess(BaseModel):
    method: Literal["approve", "reject"]
