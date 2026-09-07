import sqlite3
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime, date, time

from backend.database.models import Client, Lead, Appointment, Invoice
from backend.config import settings

# 1. Connect to SQLite
conn = sqlite3.connect('appointments.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get rows
clients_old = cur.execute("SELECT * FROM clients").fetchall()
leads_old = cur.execute("SELECT * FROM leads").fetchall()
appointments_old = cur.execute("SELECT * FROM appointments").fetchall()
invoices_old = cur.execute("SELECT * FROM invoices").fetchall()

def split_name(name: str):
    parts = name.strip().split(" ", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]

async def migrate():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # Migrate Clients
        print(f"Migrating {len(clients_old)} clients...")
        client_map = {} # old_id -> new_id
        for row in clients_old:
            first_name, last_name = split_name(row['name'])
            # check if exists
            result = await session.execute(select(Client).filter(Client.phone == row['phone']))
            existing = result.scalars().first()
            if existing:
                client_map[row['id']] = existing.id
                continue
                
            new_client = Client(
                first_name=first_name,
                last_name=last_name,
                phone=row['phone'],
                email=row['email'],
                notes=row['address'],
                is_deleted=bool(row['is_deleted'])
            )
            session.add(new_client)
            await session.commit()
            await session.refresh(new_client)
            client_map[row['id']] = new_client.id
            
        # Migrate Leads
        print(f"Migrating {len(leads_old)} leads...")
        for row in leads_old:
            first_name, last_name = split_name(row['name'])
            new_lead = Lead(
                first_name=first_name,
                last_name=last_name,
                phone=row['phone'],
                source=row['source'],
                status=row['status'],
                notes=row['notes']
            )
            session.add(new_lead)
        await session.commit()
        
        # Migrate Appointments
        print(f"Migrating {len(appointments_old)} appointments...")
        for row in appointments_old:
            if row['client_id'] not in client_map:
                continue
                
            # Parse date string: typically YYYY-MM-DD
            try:
                appt_date = datetime.strptime(row['appointment_date'], "%Y-%m-%d").date()
            except ValueError:
                # If format is weird, fallback to today
                appt_date = datetime.now().date()
                
            try:
                appt_time = datetime.strptime(row['appointment_time'], "%H:%M").time()
            except ValueError:
                appt_time = datetime.now().time()
            
            new_appt = Appointment(
                client_id=client_map[row['client_id']],
                service=row['service_type'],
                appointment_date=appt_date,
                appointment_time=appt_time,
                status=row['status'],
                is_deleted=bool(row['is_deleted'])
            )
            session.add(new_appt)
        await session.commit()
        
        # Migrate Invoices
        print(f"Migrating {len(invoices_old)} invoices...")
        for row in invoices_old:
            if row['client_id'] not in client_map:
                continue
                
            new_inv = Invoice(
                client_id=client_map[row['client_id']],
                amount=row['amount'],
                service_description="Migrated Invoice",
                is_deleted=bool(row['is_deleted'])
            )
            session.add(new_inv)
        await session.commit()
        
        print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())

