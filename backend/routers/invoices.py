from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.database.connection import get_db
from backend.database.models import Invoice
from backend.schemas.invoices import InvoiceCreate, InvoiceResponse
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

@router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Invoice).filter(Invoice.is_deleted == False))
    return result.scalars().all()

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_in: InvoiceCreate, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    new_invoice = Invoice(**invoice_in.model_dump())
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    return new_invoice
