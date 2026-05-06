import json
import logging

from fastapi import APIRouter
from scripts.config import Service
from scripts.core.constants.api import APIEndpoints
from scripts.core.handlers.default import DefaultHandler
from scripts.core.schemas.response_models import DefaultResponse

router = APIRouter(prefix="/custom_app")
handler = DefaultHandler


@router.get(APIEndpoints.load_styles)
async def load_styles():
    """
    Default: Loads required endpoints to get filenames in the build
    Do not edit this
    """
    return handler.load_styles()


@router.get(APIEndpoints.load_file)
def download_resource(filename: str):
    """Default: Request Build Files to redner widget configurations on the frontend
    Do not edit this
    """
    return handler.download_resources(filename)


@router.get(APIEndpoints.preview)
async def preview(request_type: str = "refresh"):
    """
    Request Type Options
    Preview: Can take in all widget configuration from payload and return Chart Preview Response
    Refresh: Will accept widget ID and derive the widget configuration from Widget collection, to then return the
    chart response
    """
    try:
        if request_type not in ["refresh", "preview"]:
            return DefaultResponse(message="Invalid Query Parameter")
        with open(f"{Service.BACKEND_DIR}/scripts/assets/chart_json.json") as file:
            file_content = json.loads(file.read())
        return file_content
    except Exception as e:
        logging.error(e)
        return DefaultResponse(message="Not found")


@router.get(APIEndpoints.load_configuration)
async def load_configuration():
    """
    Default: Load widget configuration JSON for listing plugins while creating widgets
    Do not edit this
    """
    return handler.load_configuration()
