"""
These are endpoints to handle
- User reporting wrong prediction result
- Operator viewing reports
"""
from typing import List

from fastapi import APIRouter, Depends

from app import schemas
from app.services.auth import OperatorAuthHandler, UserAuthHandler
from app.services.report import ReportService

router = APIRouter()
report_service = ReportService()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()


@router.get(
    "/view-reports",
    response_model=List[schemas.ReportResponse],
    name="operator:view-report",
)
def view_reports(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    report_list = report_service.get_report_list()
    return report_list


@router.post("/send-report", name="user:send-report")
def send_report(username: str, user_identifier=Depends(user_auth_handler.auth_wrapper)):
    report_service.add_report(username, reporter_id=user_identifier["user_id"])
    return None
