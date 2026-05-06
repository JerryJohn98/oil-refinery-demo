from typing import Any, Optional

from pydantic import BaseModel
from scripts.config.app_configurations import Timezone


class DefaultResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any]


class DefaultFailureResponse(BaseModel):
    status: str = "failed"
    message: str


class CommonRequest(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    tz: str = Timezone.desired_time_zone
    project_type: Optional[str] = ""
    language: Optional[str] = "en"


class CommonPaginationResponse(BaseModel):
    bodyContent: list = []
    total_no: int = 0
    endOfRecords: bool = True


class CountFilterRequest(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    tz: str = Timezone.desired_time_zone
    project_type: Optional[str] = ""
    language: Optional[str] = "en"
    site: str
    area: Optional[str]
    line: Optional[str]


class TimeCalcRequest(BaseModel):
    widget_filter: dict
    tz: str
