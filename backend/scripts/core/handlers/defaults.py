import json
import logging
import os

from fastapi.responses import FileResponse
from scripts.config import Service
from scripts.core.schemas.response_models import (
    DefaultFailureResponse,
    DefaultSuccessResponse,
    LoadStylesResponse,
)


class DefaultHandler:

    @staticmethod
    def load_styles():
        try:
            response = LoadStylesResponse()
            for each_file in os.listdir(Service.BUILD_DIR):
                path = f"{Service.PROXY}/custom_app/load_file?filename={each_file}"
                if each_file.endswith(".js"):
                    response.js_files.append(path)
                elif each_file.endswith(".css"):
                    response.styles.append(path)
                elif each_file == "assets":
                    response.assetPath = "/assets"

            return DefaultSuccessResponse(
                message="Styles loaded successfully", data=response, status="success"
            )
        except Exception as e:
            logging.exception(e)
            return DefaultFailureResponse(
                message="Failed to load file paths", status="failed"
            )

    @staticmethod
    def download_resources(filename: str):
        try:
            file_path = os.path.join(Service.BUILD_DIR, filename)
            if os.path.isfile(
                os.path.join(Service.BUILD_DIR, filename)
            ) and filename.endswith(".js"):
                return FileResponse(
                    file_path, media_type="text/javascript", filename=filename
                )
            elif os.path.isfile(
                os.path.join(Service.BUILD_DIR, filename)
            ) and filename.endswith(".css"):
                return FileResponse(file_path, media_type="text/css", filename=filename)
            else:
                return DefaultFailureResponse(message="Failed to load resources")
        except Exception as e:
            logging.error("Exception " + str(e))
            return DefaultFailureResponse(message="Filename is not available")

    @staticmethod
    def load_configuration():
        try:
            with open(f"{Service.BUILD_DIR}/assets/widgetConfig.json") as file:
                file_content = json.loads(file.read())
            return file_content
        except Exception as e:
            logging.error(e)
            return DefaultFailureResponse(message="Failed to load configurations")
