from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Any
from datetime import datetime, timedelta, date, time

from backend.database.connection import get_db
from backend.database.models import Appointment, Manager, Client
from backend.schemas.appointments import AppointmentCreate, AppointmentUpdate, AppointmentResponse, PublicBooking
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

def extract_employee(service_str: Optional[str], emp: Optional[str] = None) -> Optional[str]:
    if emp and emp.strip():
        return emp.strip()
    if not service_str:
        return None
    for name in ["דני", "דוד", "יעל", "שירן", "נועם"]:
        if name in service_str:
            return name
    return None

async def check_collision(db: AsyncSession, check_date: date, check_time: time, employee: Optional[str] = None, exclude_id: int = None) -> bool:
    """
    Checks if there's a colliding appointment within 60 minutes for the SAME employee/barber.
    If employee is specified, appointments with a different employee do not collide!
    """
    target_emp = employee.strip() if employee else None
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
            if target_emp:
                appt_emp = extract_employee(appt.service, getattr(appt, 'employee', None))
                # If existing appointment is with a different employee, it does not collide!
                if appt_emp and appt_emp != target_emp:
                    continue
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
    Create a new appointment, enforcing the 60-minute collision rule per employee.
    """
    target_emp = appt_in.employee or extract_employee(appt_in.service)
    collision = await check_collision(db, appt_in.appointment_date, appt_in.appointment_time, employee=target_emp)
    if collision:
        emp_text = f" עבור {target_emp}" if target_emp else ""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"השעה תפוסה! קיים כבר תור{emp_text} בטווח של שעה מזמן זה."
        )
        
    appt_data = appt_in.model_dump()
    if not appt_data.get("employee"):
        appt_data["employee"] = target_emp
    new_appt = Appointment(**appt_data)
    db.add(new_appt)
    await db.commit()
    await db.refresh(new_appt)
    return new_appt


@router.post("/book_public", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_public_booking(
    booking_in: PublicBooking,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Public endpoint for customers to book an appointment directly.
    Finds or creates a Client by phone, then creates the Appointment.
    """
    # 1. Check for collision per employee
    target_emp = booking_in.employee or extract_employee(booking_in.service)
    collision = await check_collision(db, booking_in.appointment_date, booking_in.appointment_time, employee=target_emp)
    if collision:
        emp_text = f" עבור {target_emp}" if target_emp else ""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"השעה תפוסה! קיים כבר תור{emp_text} בטווח של שעה מזמן זה. אנא בחר שעה אחרת."
        )
        
    # 2. Find or create client
    client_result = await db.execute(select(Client).filter(Client.phone == booking_in.phone))
    client = client_result.scalars().first()
    
    if client:
        if not client.email and booking_in.email:
            client.email = booking_in.email
        if not client.city and booking_in.city:
            client.city = booking_in.city
        await db.commit()
    
    if not client:
        client = Client(
            first_name=booking_in.first_name,
            last_name=booking_in.last_name,
            phone=booking_in.phone,
            email=booking_in.email,
            city=booking_in.city,
            source="טופס אתר",
            notes=booking_in.notes
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
    # 3. Create appointment
    new_appt = Appointment(
        client_id=client.id,
        service=booking_in.service,
        employee=target_emp,
        appointment_date=booking_in.appointment_date,
        appointment_time=booking_in.appointment_time,
        status="ממתין לאישור"
    )
    db.add(new_appt)
    await db.commit()
    await db.refresh(new_appt)
    return new_appt

@router.patch("/{appt_id}", response_model=AppointmentResponse)
async def update_appointment(
    appt_id: int,
    appt_update: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> Any:
    """
    Update an appointment's status, date, time or service.
    """
    result = await db.execute(select(Appointment).filter(Appointment.id == appt_id))
    appt = result.scalars().first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        
    update_data = appt_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appt, field, value)
        
    await db.commit()
    await db.refresh(appt)
    return appt

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

@router.get("/archive", response_model=List[AppointmentResponse])
async def get_archived_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> Any:
    result = await db.execute(select(Appointment).filter(Appointment.is_deleted == True))
    return result.scalars().all()

@router.post("/{appt_id}/restore", response_model=AppointmentResponse)
async def restore_appointment(
    appt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_manager)
) -> Any:
    result = await db.execute(select(Appointment).filter(Appointment.id == appt_id))
    appt = result.scalars().first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        
    appt.is_deleted = False
    await db.commit()
    await db.refresh(appt)
    return appt
