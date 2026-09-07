import re

with open('frontend/customer/src/app/page.tsx', 'r') as f:
    code = f.read()

old_submit = """      await axios.post(`${apiUrl}/api/appointments/book_public`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        service: bookingService,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time
      });"""

new_submit = """      await axios.post(`${apiUrl}/api/appointments/book_public`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        email: formData.email,
        service: `${formData.service_type} (עם: ${formData.employee})`,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time
      });"""

if old_submit in code:
    code = code.replace(old_submit, new_submit)
else:
    print("Warning: old_submit not found!")

with open('frontend/customer/src/app/page.tsx', 'w') as f:
    f.write(code)

with open('backend/schemas/appointments.py', 'r') as f:
    schema = f.read()

schema = schema.replace(
    "phone: str\n    service: str",
    "phone: str\n    email: str\n    service: str"
)

with open('backend/schemas/appointments.py', 'w') as f:
    f.write(schema)

print("Submit patched.")
