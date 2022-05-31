"""
These are endpoints to handle
- Adding user report as data for the ML service
"""

from fastapi import APIRouter, Depends

from app.services.auth import OperatorAuthHandler, UserAuthHandler
from app.services.ml import ML

router = APIRouter()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()


# Note: Operator only
@router.get("/add-ml-data", name="operator:add-ml-data")
def add_ml_data(
    report_id: str, user_identifier=Depends(operator_auth_handler.auth_wrapper)
):
    # TODO: Take report from db, scape needed data and add to ML's database somehow!
    return "success"


@router.get("/get-analysis-result", name="user:get-analysis-result")
def get_analysis_result(username: str):
    ml_service = ML()
    result = ml_service.get_analysis_result(username)
    return result
