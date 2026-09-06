from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    source: Optional[str] = None
    status: Optional[str] = "חדש"
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
