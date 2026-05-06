from typing import Any, Optional

from pydantic import BaseModel


class DefaultResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any]


class LoadStylesResponse(BaseModel):
    styles: list = []
    js_files: list = []
    assetPath: str = ""


class FyFilterModel(BaseModel):
    project_type: Optional[str] = "n_level_hierarchy"
    tz: Optional[str] = "Asia/Kolkata"
    project_id: str
    language: Optional[str] = "en"


class FyQPFilterModel(BaseModel):
    project_type: Optional[str] = "n_level_hierarchy"
    tz: Optional[str] = "Asia/Kolkata"
    project_id: str
    language: Optional[str] = "en"
    selected_year: str
    startdate: str
    enddate: str
