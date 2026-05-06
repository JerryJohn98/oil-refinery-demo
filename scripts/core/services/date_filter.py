import traceback

from fastapi import APIRouter, Depends
from scripts.core.constants.api import APIEndpoints
from scripts.core.handlers.date_filter import DateFilter
from scripts.core.schemas.request_model import FyFilterModel, FyQPFilterModel
from scripts.utils.security_utils.cookie_decorator import MetaInfoCookie

fy_filter_router = APIRouter()
get_cookies = MetaInfoCookie()


@fy_filter_router.post(APIEndpoints.get_fy_filter)
def get_fy_filter(
    input_json: FyFilterModel, user_id: str = Depends(get_cookies.authorize_token)
):
    try:
        payload_json = input_json.dict()
        response = DateFilter(user_id=user_id, payload=payload_json).get_fy_filter()
        return response
    except Exception as df_error:
        traceback.print_exc()
        raise df_error


@fy_filter_router.post(APIEndpoints.list_fy_filter)
def get_fy_q_filter(
    input_json: FyQPFilterModel, user_id: str = Depends(get_cookies.authorize_token)
):
    try:
        payload_json = input_json.dict()
        response = DateFilter(user_id=user_id, payload=payload_json).get_fy_qp_filter()
        return response
    except Exception as df_error:
        traceback.print_exc()
        raise df_error
