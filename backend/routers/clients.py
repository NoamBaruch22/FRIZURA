from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from backend.database.connection import get_db
from backend.database.models import Client, Appointment, Invoice
from backend.schemas.clients import ClientCreate, ClientUpdate, ClientResponse
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.get("/", response_model=List[ClientResponse])
async def get_clients(db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Client).filter(Client.is_deleted == False))
    return result.scalars().all()

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client_in: ClientCreate, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    new_client = Client(**client_in.model_dump())
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    # Soft delete client and cascade to appointments and invoices
    result = await db.execute(select(Client).filter(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    client.is_deleted = True
    # Cascade
    await db.execute(update(Appointment).where(Appointment.client_id == client_id).values(is_deleted=True))
    await db.execute(update(Invoice).where(Invoice.client_id == client_id).values(is_deleted=True))
    
    await db.commit()
