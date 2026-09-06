from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

class InvoiceBase(BaseModel):
    client_id: int
    amount: float
    service_description: str
    invoice_date: Optional[date] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    is_deleted: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
