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


# Note: Operator only
@router.get(
    "/view-reports",
    response_model=List[schemas.ReportResponse],
    name="operator:view-report",
)
# def view_reports():
def view_reports(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    report_list = report_service.get_report_list()
    return report_list


# NOTE: User only
@router.post("/send-report/{twitter_user_id}", name="user:send-report")
# def send_report(username: str):
def send_report(username: str, user_identifier=Depends(user_auth_handler.auth_wrapper)):
    report = report_service.add_report(username)

    # NOTE: remove this fake check when implemented
    # user_already_reported = randint(0, 1) == 0
    # if user_already_reported:
    #     raise HTTPException(
    #         status_code=420,
    #         detail="User already reported this Twitter Account Recently!",
    #     )
    return {"status": "success", "account": report.username}
