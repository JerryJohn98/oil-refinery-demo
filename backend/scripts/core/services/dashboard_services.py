from fastapi import APIRouter, Depends
from requests import Session
from scripts.core.constants.api import DashboardAPI
from scripts.core.handlers.dashboard_handler import DashboardHandler
from scripts.core.schemas.dashboard_model import ProcessOrderDropdownRequest
from scripts.core.schemas.response_models import DefaultFailureResponse, DefaultResponse
from scripts.db.psql.databases import get_assistant_db
from scripts.logging.logging import logger
from scripts.utils.security_utils.cookie_decorator import MetaInfoCookie

auth = MetaInfoCookie().authorize_token
dashboard_router = APIRouter(
    tags=["Diageo Dashboard Services"], prefix=DashboardAPI.prefix
)


@dashboard_router.post(DashboardAPI.get_process_order)
async def get_process_order(
    request_data: dict = Depends(auth),
    assistant_db: Session = Depends(get_assistant_db),
):
    try:
        request_data = ProcessOrderDropdownRequest(**request_data)
        production_handler = DashboardHandler(
            project_id=request_data.project_id, assistant_db=assistant_db
        )
        data = production_handler.get_process_order(request_data=request_data)
        return DefaultResponse(message="Data fetched successfully", data=data)
    except Exception as production_error:
        logger.error(f"Failed to fetch data: {production_error}")
        return DefaultFailureResponse(
            message=f"Failed to fetch data: {production_error}"
        )
