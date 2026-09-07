with open('frontend/customer/src/app/page.tsx', 'r') as f:
    code = f.read()

old_options = """    { role: 'model', content: 'שלום וברוכים הבאים למספרת FRIZURA! ✂️ איך אוכל לעזור לך היום?', options: ["לקבוע תור", "שעות פעילות", "איזה שירותים יש לכם?"] }"""
new_options = """    { role: 'model', content: 'שלום וברוכים הבאים למספרת FRIZURA! ✂️ איך אוכל לעזור לך היום?', options: ["לקבוע תור", "בדיקת תור קיים", "שעות פעילות", "איזה שירותים יש לכם?"] }"""

if old_options in code:
    code = code.replace(old_options, new_options)
    with open('frontend/customer/src/app/page.tsx', 'w') as f:
        f.write(code)
    print("Initial options updated.")
else:
    print("Failed to find old options")
