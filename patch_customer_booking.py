import re

with open('frontend/customer/src/app/page.tsx', 'r') as f:
    code = f.read()

# Update formData state initial structure to include email and employee
code = re.sub(
    r'const \[formData, setFormData\] = useState\(\{[\s\S]*?notes: ""\s*\}\);',
    'const [formData, setFormData] = useState({ first_name: "", last_name: "", phone: "", email: "", service_type: "", employee: "", appointment_date: "", appointment_time: "", notes: "" });',
    code
)

# Update the modal JSX
old_form = """              <form onSubmit={handleBookingSubmit} className="flex flex-col gap-4">
                <div className="flex gap-4">
                  <input required type="text" placeholder="שם פרטי" className="border p-2 rounded flex-1" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                  <input required type="text" placeholder="שם משפחה" className="border p-2 rounded flex-1" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                </div>
                <input required type="tel" placeholder="מספר טלפון" className="border p-2 rounded" dir="ltr" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />"""

new_form = """              <form onSubmit={handleBookingSubmit} className="flex flex-col gap-4">
                <div className="flex gap-4">
                  <input required type="text" placeholder="שם פרטי" className="border p-2 rounded flex-1" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                  <input required type="text" placeholder="שם משפחה" className="border p-2 rounded flex-1" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                </div>
                <div className="flex gap-4">
                  <input required type="tel" placeholder="מספר טלפון" className="border p-2 rounded flex-1" dir="ltr" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
                  <input required type="email" placeholder="אימייל (חובה)" className="border p-2 rounded flex-1" dir="ltr" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
                </div>
                <div className="flex gap-4">
                  <select required className="border p-2 rounded flex-1" value={formData.service_type} onChange={e => setFormData({...formData, service_type: e.target.value})}>
                    <option value="">בחר סוג שירות</option>
                    <option value="תספורת גברים / עיצוב זקן">תספורת גברים / עיצוב זקן</option>
                    <option value="תספורת נשים">תספורת נשים</option>
                    <option value="צבע / גוונים">צבע / גוונים</option>
                    <option value="החלקת קרטין / כלה">החלקת קרטין / כלה</option>
                    <option value="שיקום / כימיה">שיקום / כימיה</option>
                  </select>
                  <select required className="border p-2 rounded flex-1" value={formData.employee} onChange={e => setFormData({...formData, employee: e.target.value})}>
                    <option value="">בחר עובד.ת</option>
                    <option value="דני">דני (גברים, זקן)</option>
                    <option value="יעל">יעל (נשים, צבע)</option>
                    <option value="שירן">שירן (כלה, קרטין)</option>
                    <option value="דוד">דוד (גברים, דירוגים)</option>
                    <option value="נועם">נועם (כימיה, שיקום)</option>
                  </select>
                </div>"""

if old_form in code:
    code = code.replace(old_form, new_form)
else:
    print("Warning: old_form not found in customer frontend!")

with open('frontend/customer/src/app/page.tsx', 'w') as f:
    f.write(code)

print("Customer frontend updated.")
