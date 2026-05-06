from typing import Any, Optional

from pydantic import BaseModel


class DefaultSuccessResponse(BaseModel):
    status: str = "Success"
    message: str = "No results found"
    data: Optional[Any]


class DefaultFailureResponse(BaseModel):
    status: str = "Failed"
    message: str = "Error While Fetching Options"
