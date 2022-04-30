from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    avatar: str
    username: str
    created_at: datetime
    scrape_date: datetime
    report_count: int
    score: float


class ProcessedReportResponse(BaseModel):
    id: str
    user: dict[str, Any]
    label: int
