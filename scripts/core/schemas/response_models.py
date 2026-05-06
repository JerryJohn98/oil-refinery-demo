from typing import Any, Optional

from pydantic import BaseModel


class DefaultFailureResponse(BaseModel):
    status: str = "Failed"
    message: Optional[str]


class DefaultSuccessResponse(BaseModel):
    status: str = "success"
    message: Optional[str]
    data: Optional[Any]


class LoadStylesResponse(BaseModel):
    styles: list = []
    js_files: list = []
    assetPath: str = ""


class DefaultResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any]
