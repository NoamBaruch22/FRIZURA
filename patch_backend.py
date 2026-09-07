import os
import re

def patch_file(filepath, replacements):
    with open(filepath, 'r') as f:
        content = f.read()
    
    for target, replacement in replacements:
        if target in content:
            content = content.replace(target, replacement)
        else:
            print(f"Warning: Target string not found in {filepath}")
            
    with open(filepath, 'w') as f:
        f.write(content)

# Patching Clients Router
client_patch = """
@router.get("/archive", response_model=List[ClientResponse])
async def get_archived_clients(db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Client).filter(Client.is_deleted == True))
    return result.scalars().all()

@router.post("/{client_id}/restore", response_model=ClientResponse)
async def restore_client(client_id: int, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(Client).filter(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    client.is_deleted = False
    # Optionally restore appointments/invoices that were deleted
    await db.execute(update(Appointment).where(Appointment.client_id == client_id).values(is_deleted=False))
    await db.execute(update(Invoice).where(Invoice.client_id == client_id).values(is_deleted=False))
    await db.commit()
    await db.refresh(client)
    return client

"""
with open('backend/routers/clients.py', 'a') as f:
    f.write(client_patch)

print("Clients patched")
