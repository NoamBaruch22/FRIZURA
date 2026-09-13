import os
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai
from google.genai import types
from backend.config import settings
from backend.database.models import Client, Appointment

class ChatbotService:
    def __init__(self):
        if settings.chatbot_provider == "gemini":
            self.client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())
            self.model_id = "gemini-3.6-flash"
        self.system_prompt = """
        You are an AI assistant for FRIZURA boutique hair salon. Your role is to help customers book appointments and answer questions.
        You must speak in polite and professional Hebrew.
        
        Our team (הצוות שלנו):
        1. דני (Dani) - תספורת גברים, עיצוב זקן, פנים
        2. יעל (Yael) - תספורת נשים, צבע, גוונים, פנים
        3. שירן (Shiran) - החלקות קרטין, תסרוקות ערב וכלה
        4. דוד (David) - תספורת גברים קלאסית, דירוגים, זקן
        5. נועם (Noam) - כימיה לשיער, שיקום שיער, תספורות נשים מיוחדות
        
        Critical Hebrew Terminology Rule:
        - NEVER write "אחה״כ" when referring to times of day (afternoon)!
        - ALWAYS write "אחה״צ" (קיצור של אחר הצהריים). For example: "בשעות הבוקר או אחה״צ?", "יש תור ב-16:00 אחה״צ".
        
        Step-by-Step Booking Flow Guidelines (Ask ONE question at a time):
        Step 1 - Service: Ask if they want a men's or women's haircut/service, or what specific service they need.
        Step 2 - Stylist/Barber: Suggest relevant staff members for that service (Dani/David for men, Yael/Shiran/Noam for women).
        Step 3 - Date and Time: Ask for preferred date and time (Remember: use "אחה״צ" for afternoon, never "אחה״כ").
        Step 4 - Full Name and Phone: Ask for client's full name (first and last) and mobile phone number.
        Step 5 - Valid Email Address: Ask for a valid email address ("מהי כתובת הדוא״ל (אימייל) שלך לקבלת אישור התור?").
                 Validate that it has an '@' and a domain (e.g. name@example.com). If the input is not a valid email, politely ask again for a valid email address.
        Step 6 - City: Ask explicitly: "תרצה להוסיף עיר מגורים?" with options: ["דלג", "תל אביב", "אזור", "חולון", "ראשון לציון"] (or user can type any city).
        Step 7 - Notes: Ask explicitly: "תרצה להוסיף הערה כלשהי?" with options: ["ללא הערות", "בקשה מיוחדת"] (or user can type any note).
        Step 8 - Execution: Once you have all the information (service, barber, date in YYYY-MM-DD, time in HH:MM, name, phone, valid email, city, notes), execute the "book_appointment" action!
        
        You have internal tools to check, book, and update appointments!
        If a user asks "מתי התור שלי?" (When is my appointment?), ask for their phone number.
        Once you have their phone number, output an action in your JSON to check the DB.
        If a user asks to change the date/time of an existing appointment, use the update action.
        When booking a new appointment for a client, use "book_appointment".
        
        CRITICAL: Your output MUST be ONLY valid JSON matching this structure:
        {
           "reply": "Your response text in Hebrew",
           "options": ["Option 1", "Option 2"],
           "action": {"name": "none"},
           "calendar_event": null
        }
        
        To check an appointment, set action:
        "action": {"name": "check_appointments", "phone": "0542222667"}
        
        To update an appointment, set action:
        "action": {"name": "update_appointment", "appointment_id": 12, "new_date": "2026-10-01", "new_time": "14:30"}
        
        To book a new appointment, set action:
        "action": {
            "name": "book_appointment", 
            "first_name": "ישראל", 
            "last_name": "ישראלי", 
            "phone": "0501234567", 
            "email": "israel@gmail.com", 
            "city": "תל אביב", 
            "notes": "שיער ארוך",
            "service": "תספורת גברים וזקן (עם: דני)", 
            "employee": "דני",
            "appointment_date": "2026-10-15", 
            "appointment_time": "14:00"
        }
        
        When an appointment is successfully booked or confirmed:
        - Include the "calendar_event" object in your JSON:
        "calendar_event": {
           "title": "תור למספרת FRIZURA - תספורת גברים וזקן (עם: דני)",
           "date": "2026-10-15",
           "time": "14:00",
           "duration_minutes": 60,
           "location": "קפלן 5, אזור",
           "description": "תור למספרת FRIZURA עבור ישראל ישראלי. שירות: תספורת גברים וזקן (עם: דני). טלפון לבירורים: 054-2002400."
        }
        - In "reply", confirm all booking details and state that they can add it to Google Calendar using the button in the calendar card below 📅.
        - In "options", provide simple follow-up options like: ["תודה רבה!", "קביעת תור נוסף"].
          DO NOT put "הוסף ליומן Google" in options, as the calendar card widget already has the action button!
        
        If you set an action other than "none", the system will intercept it, run the DB query, and provide you the result in the next message so you can reply to the user.
        Do not wrap the JSON in Markdown code blocks like ```json.
        """

    async def check_appointments(self, db: AsyncSession, phone: str) -> str:
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

    async def update_appointment(self, db: AsyncSession, appointment_id: int, new_date: str, new_time: str) -> str:
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

    async def book_appointment(self, db: AsyncSession, data: dict) -> str:
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip() or "לקוח"
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip() or None
        city = data.get("city", "").strip() or None
        if city and any(k in city for k in ["דלג", "ללא", "אין", "לא"]):
            city = None
        notes = data.get("notes", "").strip() or None
        if notes and any(k in notes for k in ["ללא", "אין", "דלג", "לא"]):
            notes = None
        service = data.get("service", "תספורת כללית")
        date_str = data.get("appointment_date", "")
        time_str = data.get("appointment_time", "")

        if not phone or not date_str or not time_str:
            return json.dumps({"status": "error", "message": "Missing required booking details (phone, date, or time)."})

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            # Support both HH:MM and HH:MM:SS
            if len(time_str) == 5:
                parsed_time = datetime.strptime(time_str, "%H:%M").time()
            else:
                parsed_time = datetime.strptime(time_str[:5], "%H:%M").time()
        except ValueError:
            return json.dumps({"status": "error", "message": "Invalid date or time format. Expected YYYY-MM-DD and HH:MM."})

        # Determine target employee
        target_emp = data.get("employee")
        if not target_emp:
            for emp_name in ["דני", "דוד", "יעל", "שירן", "נועם"]:
                if emp_name in service:
                    target_emp = emp_name
                    break

        # Check collision within 60 minutes for the same employee
        stmt = select(Appointment).filter(
            Appointment.appointment_date == parsed_date,
            Appointment.is_deleted == False,
            Appointment.status != "בוטל"
        )
        existing_appts = (await db.execute(stmt)).scalars().all()
        check_dt = datetime.combine(parsed_date, parsed_time)
        for appt in existing_appts:
            appt_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
            if abs((check_dt - appt_dt).total_seconds()) < 3600:
                # Check if appt has a different employee
                appt_emp = getattr(appt, 'employee', None)
                if not appt_emp:
                    for emp_name in ["דני", "דוד", "יעל", "שירן", "נועם"]:
                        if emp_name in appt.service:
                            appt_emp = emp_name
                            break
                if target_emp and appt_emp and target_emp != appt_emp:
                    continue # Not the same employee, no collision!
                return json.dumps({"status": "collision", "message": f"There is already an appointment with {target_emp or 'the stylist'} within 60 minutes of this time. Please pick another time."})

        # Find or create client
        client = (await db.execute(select(Client).filter(Client.phone == phone))).scalars().first()
        if client:
            if email and not client.email:
                client.email = email
            if city and not client.city:
                client.city = city
            if notes:
                client.notes = f"{client.notes}\n{notes}" if client.notes else notes
            await db.commit()
        else:
            client = Client(
                first_name=first_name or "לקוח",
                last_name=last_name,
                phone=phone,
                email=email,
                city=city,
                source="צ׳אט בוט",
                notes=notes or "נוצר אוטומטית באמצעות הצ׳אט בוט של FRIZURA"
            )
            db.add(client)
            await db.commit()
            await db.refresh(client)

        new_appt = Appointment(
            client_id=client.id,
            service=service,
            employee=target_emp,
            appointment_date=parsed_date,
            appointment_time=parsed_time,
            status="ממתין לאישור"
        )
        db.add(new_appt)
        await db.commit()
        await db.refresh(new_appt)

        return json.dumps({
            "status": "success",
            "appointment_id": new_appt.id,
            "client_name": f"{client.first_name} {client.last_name}",
            "service": service,
            "employee": target_emp,
            "date": parsed_date.isoformat(),
            "time": parsed_time.strftime("%H:%M"),
            "location": "קפלן 5, אזור"
        })

    def _sanitize_response(self, res_dict: dict) -> dict:
        def clean_txt(t: str) -> str:
            if not isinstance(t, str):
                return t
            return t.replace("אחה״כ", "אחה״צ").replace("אחה\"כ", "אחה״צ").replace("אחהכ", "אחה״צ")

        if isinstance(res_dict, dict):
            if "reply" in res_dict:
                res_dict["reply"] = clean_txt(res_dict["reply"])
            if "options" in res_dict and isinstance(res_dict["options"], list):
                res_dict["options"] = [clean_txt(opt) for opt in res_dict["options"]]
        return res_dict

    async def process_chat(self, db: AsyncSession, phone: str, messages: list):
        history = []
        for m in messages:
            if m.role == "user":
                history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"<user_input>{m.content}</user_input>")]))
            else:
                history.append(types.Content(role="model", parts=[types.Part.from_text(text=json.dumps({"reply": m.content, "options": m.options if hasattr(m, 'options') else []}, ensure_ascii=False))]))
                
        return await self._generate_with_actions(db, history, depth=0)

    async def _generate_with_actions(self, db: AsyncSession, history, depth=0):
        if depth > 3:
            return {"reply": "מצטערים, התהליך מורכב מדי כרגע.", "options": []}
            
        try:
            import asyncio
            response = None
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=history,
                        config=types.GenerateContentConfig(
                            system_instruction=self.system_prompt,
                            temperature=0.7,
                            response_mime_type="application/json"
                        )
                    )
                    break
                except Exception as inner_e:
                    if "503" in str(inner_e) and attempt < 2:
                        await asyncio.sleep(1.5)
                        continue
                    raise inner_e
                    
            data = json.loads(response.text)
            
            action = data.get("action", {})
            action_name = action.get("name", "none")
            
            if action_name == "none":
                return self._sanitize_response(data)
                
            # Execute the action!
            history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
            
            action_result = ""
            if action_name == "check_appointments":
                action_result = await self.check_appointments(db, action.get("phone", ""))
            elif action_name == "update_appointment":
                action_result = await self.update_appointment(
                    db,
                    action.get("appointment_id", 0), 
                    action.get("new_date", ""), 
                    action.get("new_time", "")
                )
            elif action_name == "book_appointment":
                action_result = await self.book_appointment(db, action)
            else:
                action_result = json.dumps({"status": "error", "message": "Unknown action"})
                
            # Feed result back to model as a user message (system simulation)
            history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"<system_tool_result>{action_result}</system_tool_result> Please summarize this for the user in Hebrew. Confirm the appointment and tell them they can click the calendar card below to save it in Google Calendar.")]))
            
            # Recurse
            recurse_res = await self._generate_with_actions(db, history, depth + 1)
            # If book_appointment was successful, ensure calendar_event is present
            if action_name == "book_appointment":
                try:
                    parsed_res = json.loads(action_result)
                    if parsed_res.get("status") == "success":
                        recurse_res["calendar_event"] = {
                            "title": f"תור למספרת FRIZURA - {parsed_res.get('service')}",
                            "date": parsed_res.get("date"),
                            "time": parsed_res.get("time"),
                            "duration_minutes": 60,
                            "location": "קפלן 5, אזור",
                            "description": f"תור ב-FRIZURA עבור {parsed_res.get('client_name')}. שירות: {parsed_res.get('service')}. טלפון לבירורים: 054-2002400."
                        }
                        # Clean options so no duplicate calendar buttons appear in options
                        clean_opts = [
                            opt for opt in recurse_res.get("options", [])
                            if not any(k in opt for k in ["יומן", "Google", "גוגל", "calendar"])
                        ]
                        if not clean_opts:
                            clean_opts = ["תודה רבה!", "קביעת תור נוסף"]
                        recurse_res["options"] = clean_opts
                except Exception:
                    pass
            return self._sanitize_response(recurse_res)
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "reply": "מצטערים, המערכת החכמה שלנו חווה כרגע עומס זמני.",
                "options": []
            }
