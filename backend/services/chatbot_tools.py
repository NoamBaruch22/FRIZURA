import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from backend.config import settings
from backend.database.models import Client, Appointment

engine = create_async_engine(settings.database_url, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def _check_appointments(phone: str) -> str:
    async with async_session() as db:
        client = (await db.execute(select(Client).filter(Client.phone == phone))).scalars().first()
        if not client:
            return json.dumps({"status": "not_found", "message": "No client found with this phone number."})
            
        appointments = (await db.execute(select(Appointment).filter(
            Appointment.client_id == client.id,
            Appointment.is_deleted == False
        ))).scalars().all()
        
        if not appointments:
            return json.dumps({"status": "not_found", "message": "No appointments found for this client."})
            
        results = []
        for appt in appointments:
            results.append({
                "appointment_id": appt.id,
                "date": appt.appointment_date.isoformat(),
                "time": appt.appointment_time.isoformat(),
                "service": appt.service,
                "status": appt.status
            })
            
        return json.dumps({"status": "success", "client_name": f"{client.first_name} {client.last_name}", "appointments": results})

def check_appointments(phone: str) -> str:
    """
    Search for a customer's upcoming appointments using their phone number.
    Returns a JSON string containing the appointments or a not found message.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_check_appointments(phone))

async def _update_appointment(appointment_id: int, new_date: str, new_time: str) -> str:
    async with async_session() as db:
        appt = (await db.execute(select(Appointment).filter(Appointment.id == appointment_id))).scalars().first()
        if not appt:
            return json.dumps({"status": "error", "message": "Appointment not found."})
            
        try:
            parsed_date = datetime.strptime(new_date, "%Y-%m-%d").date()
            parsed_time = datetime.strptime(new_time, "%H:%M").time()
        except ValueError:
            return json.dumps({"status": "error", "message": "Invalid date or time format. Use YYYY-MM-DD and HH:MM."})
            
        appt.appointment_date = parsed_date
        appt.appointment_time = parsed_time
        
        await db.commit()
        return json.dumps({"status": "success", "message": "Appointment updated successfully."})

def update_appointment(appointment_id: int, new_date: str, new_time: str) -> str:
    """
    Update the date and time of an existing appointment.
    new_date MUST be in YYYY-MM-DD format.
    new_time MUST be in HH:MM format.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_update_appointment(appointment_id, new_date, new_time))
