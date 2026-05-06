import json
from scripts.core.schemas.response_models import (
    DefaultFailureResponse,
    DefaultSuccessResponse,
)


def default_response(data, message="Data fetched successfully"):
    if isinstance(data, str):
        return DefaultFailureResponse(message=data)
    return DefaultSuccessResponse(message=message, data=data)


class CommonUtils:
    def __init__(self, project_id=None, assistant_pg_obj=None):
        self.project_id = project_id
        self.assistant_pg_obj = assistant_pg_obj

    @staticmethod
    def load_json_from_file(file_path):
        with open(file_path) as f:
            return json.loads(f.read())
