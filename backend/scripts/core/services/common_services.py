from fastapi import APIRouter, Depends
from scripts.core.constants.api import CommonAPI
from scripts.core.handlers.common_handler import CommonHandler
from scripts.core.schemas.common_model import (
    CommonRequest,
    DefaultFailureResponse,
    DefaultResponse,
)
from scripts.logging.logging import logger
from scripts.utils.security_utils.cookie_decorator import MetaInfoCookie

auth = MetaInfoCookie().authorize_token
common_router = APIRouter(tags=["Common Services"], prefix=CommonAPI.prefix)


@common_router.post(CommonAPI.get_project_configurations)
async def get_project_config(request_data: dict = Depends(auth)):
    try:
        request_data = CommonRequest(**request_data)
        common_handler = CommonHandler(project_id=request_data.project_id)
        data = common_handler.get_project_configuration_handler(
            request_data=request_data
        )
        return DefaultResponse(message="Data fetched successfully", data=data)
    except Exception as common_error:
        logger.error(f"Failed to fetch data: {common_error}")
        return DefaultFailureResponse(message=f"Failed to fetch data: {common_error}")
