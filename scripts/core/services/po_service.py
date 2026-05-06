import logging
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from scripts.core.constants.api import CalculationCycleAPIs
from scripts.core.handlers.po_handler import POHandler
from scripts.core.schemas.response_models import DefaultSuccessResponse, DefaultFailureResponse
from scripts.core.schemas.po_model import ProcessOrderDropdownRequest, CalculationCycleDropdown
from scripts.core.utils.security_utils.cookie_decorator import MetaInfoCookie
from scripts.db.psql.databases import get_assistant_db, get_event_db, get_ilens_oee_db, get_shift_planning_db
from scripts.core.utils.common_utils import default_response


logger = logging.getLogger(__name__)
po_service_router = APIRouter(prefix="/calculation_cycle")

auth = MetaInfoCookie().authorize_token


@po_service_router.post(CalculationCycleAPIs.calculation_cycle_dropdown)
async def calculation_cycle_dropdown(
        request_data: dict = Depends(auth),
        assistant_db: Session = Depends(get_assistant_db),
        event_db: Session = Depends(get_event_db),
        shift_planning_db: Session = Depends(get_shift_planning_db),
):
    try:
        request_data_obj = CalculationCycleDropdown(**request_data)
        calculation_cycle_handler = POHandler(request_data_obj.project_id,assistant_db=assistant_db,shift_planning_db=shift_planning_db)
        data = calculation_cycle_handler.fetch_calculation_cycle_dropdown_data(request_data_obj)
        return default_response(data)
    except ValueError as ve:
        logger.error(f"Validation error: {ve}", exc_info=True)
        return DefaultFailureResponse(message=f"Validation error: {ve}")

    except Exception as fetch_error:
        logger.error(f"Failed to fetch calculation cycle dropdown: {fetch_error}", exc_info=True)
        return DefaultFailureResponse(message="An unexpected error occurred")


@po_service_router.post(CalculationCycleAPIs.get_po)
async def get_process_order(
    request_data: ProcessOrderDropdownRequest = Depends(auth),
    assistant_db: Session = Depends(get_assistant_db),
    oee_db: Session = Depends(get_ilens_oee_db),
    shift_planning_db: Session = Depends(get_shift_planning_db),
):
    try:
        logger.info(f"Type of request_data: {type(request_data)}")
        logger.info(f"request_data content: {request_data}")

        if isinstance(request_data, dict):
            request_data = ProcessOrderDropdownRequest(**request_data)

        po_handler = POHandler(
            project_id=request_data.project_id,
            assistant_db=assistant_db,
            oee_db=oee_db,
            shift_planning_db=shift_planning_db
        )
        data = po_handler.get_process_order(request_data=request_data)
        return default_response(data=data)
    except Exception as error:
        logger.error(f"Failed to fetch PO data: {error}", exc_info=True)
        return DefaultFailureResponse(message=str(error))
