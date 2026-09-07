import re

def create_time_options():
    options = ['<option value="">בחר שעה</option>']
    for h in range(8, 20):
        for m in ['00', '30']:
            t = f"{h:02d}:{m}"
            options.append(f'<option value="{t}">{t}</option>')
    return "\n".join(options)

time_options = create_time_options()

with open('frontend/customer/src/app/page.tsx', 'r') as f:
    customer_code = f.read()

# Replace time input in customer with select
customer_code = re.sub(
    r'<input required type="time" className="border p-2 rounded flex-1".*?/>',
    f'<select required className="border p-2 rounded flex-1" value={{formData.appointment_time}} onChange={{e => setFormData({{...formData, appointment_time: e.target.value}})}}>\n{time_options}\n</select>',
    customer_code
)

with open('frontend/customer/src/app/page.tsx', 'w') as f:
    f.write(customer_code)


with open('frontend/manager/src/app/page.tsx', 'r') as f:
    manager_code = f.read()

manager_code = re.sub(
    r'<input type="time" required className="border p-2 rounded" onChange=\{e => setFormData\(\{\.\.\.formData, appointment_time: e\.target\.value\+.:00.\}\)\} />',
    f'<select required className="border p-2 rounded" value={{formData.appointment_time?.substring(0,5) || ""}} onChange={{e => setFormData({{...formData, appointment_time: e.target.value+":00"}})}}>\n{time_options}\n</select>',
    manager_code
)

# Now, add Working Hours UI to Manager Settings
old_settings_form = """              <div>
                <label className="font-bold text-gray-700 block mb-1">טלפון</label>
                <input type="text" className="border p-2 rounded w-full bg-gray-50 focus:bg-white" value={settings.phone || ''} onChange={e => setSettings({...settings, phone: e.target.value})} dir="ltr" />
              </div>
              <button type="submit" className="bg-[#c9a962] text-white py-2 px-4 rounded hover:bg-yellow-600 self-start mt-2">שמור שינויים</button>"""

new_settings_form = f"""              <div>
                <label className="font-bold text-gray-700 block mb-1">טלפון</label>
                <input type="text" className="border p-2 rounded w-full bg-gray-50 focus:bg-white" value={{settings.phone || ''}} onChange={{e => setSettings({{...settings, phone: e.target.value}})}} dir="ltr" />
              </div>
              
              <div className="mt-4 border-t pt-4">
                <label className="font-bold text-gray-700 block mb-3">שעות פעילות (ימי עבודה)</label>
                {{['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי'].map(day => (
                  <div key={{day}} className="flex items-center gap-3 mb-2">
                    <span className="w-16">{{day}}</span>
                    <label className="flex items-center gap-1 text-sm">
                      <input type="checkbox" 
                        checked={{settings.working_hours?.[day]?.active ?? true}} 
                        onChange={{e => setSettings({{...settings, working_hours: {{...(settings.working_hours||{{}}), [day]: {{...(settings.working_hours?.[day]||{{}}), active: e.target.checked}}}}}})}} 
                      /> פעיל
                    </label>
                    <select 
                      className="border rounded p-1 text-sm" 
                      value={{settings.working_hours?.[day]?.start || '09:00'}}
                      onChange={{e => setSettings({{...settings, working_hours: {{...(settings.working_hours||{{}}), [day]: {{...(settings.working_hours?.[day]||{{}}), start: e.target.value}}}}}})}}
                      disabled={{!(settings.working_hours?.[day]?.active ?? true)}}
                    >
                      {time_options.replace('<option value="">בחר שעה</option>', '')}
                    </select>
                    <span>עד</span>
                    <select 
                      className="border rounded p-1 text-sm" 
                      value={{settings.working_hours?.[day]?.end || '18:00'}}
                      onChange={{e => setSettings({{...settings, working_hours: {{...(settings.working_hours||{{}}), [day]: {{...(settings.working_hours?.[day]||{{}}), end: e.target.value}}}}}})}}
                      disabled={{!(settings.working_hours?.[day]?.active ?? true)}}
                    >
                      {time_options.replace('<option value="">בחר שעה</option>', '')}
                    </select>
                  </div>
                ))}}
              </div>

              <button type="submit" className="bg-[#c9a962] text-white py-2 px-4 rounded hover:bg-yellow-600 self-start mt-4">שמור שינויים</button>"""

if old_settings_form in manager_code:
    manager_code = manager_code.replace(old_settings_form, new_settings_form)
else:
    print("Warning: old_settings_form not found!")

with open('frontend/manager/src/app/page.tsx', 'w') as f:
    f.write(manager_code)

print("Patch complete")
