from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    source: Optional[str] = "מנהל ידני"
    notes: Optional[str] = None

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    city: Optional[str] = None
    source: Optional[str] = "מנהל ידני"
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    is_deleted: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
