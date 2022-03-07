"""
These are endpoints to handle
- User reporting wrong prediction result
- Operator viewing reports
"""

from fastapi import APIRouter, Depends

from app import schemas
from app.services.auth import OperatorAuthHandler, UserAuthHandler

router = APIRouter()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()

# Note: Operator only


@router.get(
    "/view-reports", response_model=schemas.AccountReport, name="operator:view-report"
)
def view_reports(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    """
    TODO:
    - Take report from DB
    - Show needed information
    """
    return [{"name": "report 1"}, {"name": "report 2"}]


# NOTE: User only
@router.post("/send-report", name="user:send-report")
def send_report(
    account_id: str, user_identifier=Depends(user_auth_handler.auth_wrapper)
):
    """
    TODO:
    1. If first report:
        - Fetch account info from database or scrape
        - Copy all needed into DB (Report table)
        - Include a timestamp for the report
        - Set report count as 1
    2. Else:
        - Increase report count
    """
    return {"status": "success", "account": "twitter_account_1"}
