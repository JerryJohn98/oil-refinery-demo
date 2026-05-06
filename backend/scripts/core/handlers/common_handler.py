from scripts.core.constants.app_constants import CommonConstants
from scripts.logging.logging import logger


class CommonHandler:
    def __init__(self, project_id=None):
        self.project_id = project_id

    def get_project_configuration_handler(self, request_data):
        try:
            logger.info(request_data)
            final_data = {
                "pagination_count": CommonConstants.pagination_size,
            }
            return final_data
        except Exception as production_types:
            logger.error(f"Failed to fetch production types: {production_types}")
            raise production_types
