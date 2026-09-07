with open('backend/routers/appointments.py', 'r') as f:
    code = f.read()

old_client = """        client = Client(
            first_name=booking_in.first_name,
            last_name=booking_in.last_name,
            phone=booking_in.phone,
            notes="Auto-created from public booking"
        )"""

new_client = """        client = Client(
            first_name=booking_in.first_name,
            last_name=booking_in.last_name,
            phone=booking_in.phone,
            email=booking_in.email,
            notes="Auto-created from public booking"
        )"""

if old_client in code:
    code = code.replace(old_client, new_client)
else:
    print("Warning: old_client not found in appointments router!")

# Also, update if client exists but doesn't have an email
old_if = """    if not client:
        client = Client("""
        
new_if = """    if client and not client.email and booking_in.email:
        client.email = booking_in.email
        await db.commit()
    
    if not client:
        client = Client("""

code = code.replace(old_if, new_if)

with open('backend/routers/appointments.py', 'w') as f:
    f.write(code)

print("Endpoint patched.")
