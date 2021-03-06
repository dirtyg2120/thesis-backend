"""
These are endpoints to handle
- User reporting wrong prediction result
- Operator viewing reports
"""
import secrets
from typing import List, Optional

from fastapi import APIRouter, Cookie, Depends, Response

from app import schemas
from app.core.config import settings
from app.services.auth import OperatorAuthHandler
from app.services.report import ReportService

router = APIRouter()
operator_auth_handler = OperatorAuthHandler()


@router.get(
    "/view-reports",
    response_model=schemas.ReportResponse,
    name="operator:view-report",
)
def view_reports(
    user_identifier=Depends(operator_auth_handler.auth_wrapper),
):
    report_service = ReportService()
    report_list = report_service.get_report_list()
    return report_list


# NOTE: User only
@router.post("/send-report/{twitter_user_id}", name="user:send-report")
def send_report(
    twitter_user_id: str,
    session_id: Optional[str] = Cookie(None),
):
    report_service = ReportService()
    init_session = False
    if session_id is None:
        session_id = secrets.token_hex()
        init_session = True

    report_service.add_report(twitter_user_id, reporter_id=session_id)

    if init_session:
        resp = Response()
        resp.set_cookie(
            "session_id",
            session_id,
            max_age=settings.TOKEN_EXPIRATION_TIME * 60,
        )
        return resp


@router.post("/approve-report/{twitter_user_id}", name="user:approve-report")
def approve_report(
    twitter_user_id: str,
    user_identifier=Depends(operator_auth_handler.auth_wrapper),
):
    report_service = ReportService()
    report_service.approve_report(twitter_user_id)
    return "success"


@router.post("/reject-report/{twitter_user_id}", name="user:reject-report")
def reject_report(
    twitter_user_id: str,
    user_identifier=Depends(operator_auth_handler.auth_wrapper),
):
    report_service = ReportService()
    report_service.reject_report(twitter_user_id)
    return "success"


@router.get(
    "/export",
    response_model=List[schemas.ProcessedReportResponse],
    name="user:export-detail",
)
def export_profile(
    user_identifier=Depends(operator_auth_handler.auth_wrapper),
):
    report_service = ReportService()
    return report_service.export()
