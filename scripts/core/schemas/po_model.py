from typing import Optional
from scripts.config.app_configurations import Timezone
from pydantic import BaseModel


class HierarchyData(BaseModel):
    type: Optional[str] = ""
    filterData: Optional[dict] = {}
    filters: Optional[list] = []


class CommonRequest(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    tz: str = Timezone.desired_time_zone
    project_type: Optional[str] = ""
    language: Optional[str] = "en"


class ProcessOrderDropdownRequest(CommonRequest):
    selected_hierarchy: HierarchyData
    calculation_cycle: Optional[str] = ""


class CalculationCycleDropdown(BaseModel):
    project_type: Optional[str] = ''
    tz: Optional[str] = ''
    project_id: Optional[str] = ''
    user_id: Optional[str] = ''
