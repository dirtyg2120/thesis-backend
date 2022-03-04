from fastapi import APIRouter, Depends, HTTPException, Response

from app import schemas
from app.services.auth import OperatorAuthHandler, UserAuthHandler

router = APIRouter()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()

'''
    These are endpoints to handle
    - Adding user report as data for the ML service
'''

# Note: Operator only
@router.get(
    "/add-ml-data",name="operator:add-ml-data"
)
def add_ml_data(report_id: str, user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    # TODO: Take report from db, scape needed data and add to ML's database somehow!
    return 'success'