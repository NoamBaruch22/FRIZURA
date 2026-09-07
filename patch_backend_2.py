patch_appt = """
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
"""
with open('backend/routers/appointments.py', 'a') as f:
    f.write(patch_appt)


patch_inv = """
@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Invoice).filter(Invoice.id == invoice_id))
    inv = result.scalars().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv.is_deleted = True
    await db.commit()

@router.get("/archive", response_model=List[InvoiceResponse])
async def get_archived_invoices(db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Invoice).filter(Invoice.is_deleted == True))
    return result.scalars().all()

@router.post("/{invoice_id}/restore", response_model=InvoiceResponse)
async def restore_invoice(invoice_id: int, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Invoice).filter(Invoice.id == invoice_id))
    inv = result.scalars().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv.is_deleted = False
    await db.commit()
    await db.refresh(inv)
    return inv
"""
with open('backend/routers/invoices.py', 'a') as f:
    f.write(patch_inv)
print("Done")
