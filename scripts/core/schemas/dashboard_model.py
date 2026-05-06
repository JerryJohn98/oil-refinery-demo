from typing import Optional

from pydantic import BaseModel
from scripts.core.schemas.common_model import CommonRequest


class HierarchyData(BaseModel):
    type: Optional[str] = ""
    filterData: Optional[dict] = {}
    filters: Optional[list] = []


class ProcessOrderDropdownRequest(CommonRequest):
    selected_hierarchy: HierarchyData


class WidgetFilterModel(BaseModel):
    timePickerValue: dict
