from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.database.connection import get_db
from backend.database.models import Lead, Client
from backend.schemas.leads import LeadCreate, LeadUpdate, LeadResponse
from backend.schemas.clients import ClientResponse
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/leads", tags=["Leads"])

@router.get("/", response_model=List[LeadResponse])
async def get_leads(db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Lead))
    return result.scalars().all()

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_in: LeadCreate, db: AsyncSession = Depends(get_db)):
    # Public endpoint (no auth needed for landing page form)
    new_lead = Lead(**lead_in.model_dump())
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

@router.post("/{lead_id}/convert", response_model=ClientResponse)
async def convert_lead(lead_id: int, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Lead).filter(Lead.id == lead_id))
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if lead.status == "הפך ללקוח":
        raise HTTPException(status_code=400, detail="Lead already converted")
        
    # Atomic conversion
    new_client = Client(
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone=lead.phone,
        notes=f"Converted from lead. Source: {lead.source}"
    )
    lead.status = "הפך ללקוח"
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client
