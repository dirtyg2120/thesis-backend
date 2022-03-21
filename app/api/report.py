"""
These are endpoints to handle
- User reporting wrong prediction result
- Operator viewing reports
"""
import secrets
from typing import List, Optional

from fastapi import APIRouter, Cookie, Depends, HttpException, Response

from app import schemas
from app.core.config import settings
from app.models import AnonymousSession
from app.services.auth import OperatorAuthHandler
from app.services.report import ReportService

router = APIRouter()
operator_auth_handler = OperatorAuthHandler()


@router.get(
    "/view-reports",
    response_model=List[schemas.ReportResponse],
    name="operator:view-report",
)
def view_reports(
    user_identifier=Depends(operator_auth_handler.auth_wrapper),
    report_service: ReportService = Depends(),
):
    report_list = report_service.get_report_list()
    return report_list


# NOTE: User only
@router.post("/send-report/{twitter_user_id}", name="user:send-report")
def send_report(
    twitter_user_id: str,
    session_id: Optional[str] = Cookie(None),
    report_service: ReportService = Depends(),
):
    if session_id is None:
        session_id = secrets.token_hex()
        AnonymousSession(session_id=session_id).save()
        init_session = True
    else:
        session = AnonymousSession.objects(session_id=session_id).first()
        if session is None:
            raise HttpException(401, "Invalid session ID")
        init_session = False

    report_service.add_report(twitter_user_id, reporter_id=session_id)

    if init_session:
        resp = Response()
        resp.set_cookie(
            "session_id",
            session_id,
            max_age=settings.TOKEN_EXPIRATION_TIME * 60,
        )
        return resp
