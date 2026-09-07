from pydantic import BaseModel, ConfigDict
from datetime import date, time, datetime
from typing import Optional

class AppointmentBase(BaseModel):
    client_id: int
    service: str
    appointment_date: date
    appointment_time: time
    status: Optional[str] = "ממתין"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    service: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    is_deleted: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PublicBooking(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    service: str
    appointment_date: date
    appointment_time: time
