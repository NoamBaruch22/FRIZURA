from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class BusinessSettingsBase(BaseModel):
    business_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    services: List[str] = []
    employees: List[str] = []
    working_hours: Dict[str, Any] = {}

class BusinessSettingsUpdate(BusinessSettingsBase):
    pass

class BusinessSettingsResponse(BusinessSettingsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
