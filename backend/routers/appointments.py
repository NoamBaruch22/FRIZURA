from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Any
from datetime import datetime, timedelta, date, time

from backend.database.connection import get_db
from backend.database.models import Appointment, Manager
from backend.schemas.appointments import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

async def check_collision(db: AsyncSession, check_date: date, check_time: time, exclude_id: int = None) -> bool:
    """
    Checks if there's a colliding appointment within 60 minutes.
    """
    # SQLite didn't have great time math, but Postgres does. 
    # To keep it simple in Python, we'll fetch today's appointments and check.
    # In a production environment with massive data, we'd use raw SQL for time overlap,
    # but for a boutique salon, fetching a day's appointments is ~10-20 rows.
    
    stmt = select(Appointment).filter(
        Appointment.appointment_date == check_date,
        Appointment.is_deleted == False,
        Appointment.status != "בוטל"
    )
    result = await db.execute(stmt)
    day_appointments = result.scalars().all()
    
    check_dt = datetime.combine(check_date, check_time)
    
    for appt in day_appointments:
        if exclude_id and appt.id == exclude_id:
            continue
            
        appt_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
        diff = abs((check_dt - appt_dt).total_seconds())
        if diff < 3600: # 60 minutes
            return True
            
    return False

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> Any:
    """
    Get all active appointments.
    """
    result = await db.execute(select(Appointment).filter(Appointment.is_deleted == False))
    return result.scalars().all()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appt_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> Any:
    """
    Create a new appointment, enforcing the 60-minute collision rule.
    """
    collision = await check_collision(db, appt_in.appointment_date, appt_in.appointment_time)
    if collision:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already an appointment scheduled within 60 minutes of this time."
        )
        
    new_appt = Appointment(**appt_in.model_dump())
    db.add(new_appt)
    await db.commit()
    await db.refresh(new_appt)
    return new_appt

@router.delete("/{appt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> None:
    """
    Soft delete an appointment.
    """
    result = await db.execute(select(Appointment).filter(Appointment.id == appt_id))
    appt = result.scalars().first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        
    appt.is_deleted = True
    await db.commit()
