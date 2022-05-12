from datetime import datetime
from typing import Any, List

from pydantic import BaseModel


class CommonReport(BaseModel):
    id: str
    avatar: str
    username: str
    created_at: datetime


class ApprovedReport(CommonReport):
    label: int


class WaitingReport(CommonReport):
    score: float
    scrape_date: datetime
    report_count: int


class ReportResponse(BaseModel):
    waiting: List[WaitingReport]
    approved: List[ApprovedReport]


class ProcessedReportResponse(BaseModel):
    user_id: str
    user: Any
    tweet_graph: Any
    label: int
