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
        
        Important Booking Flow Guidelines:
        1. Guide the user through booking by asking ONE question at a time.
        2. First ask if they want a men's or women's service, or what specific service they need.
        3. Then suggest the relevant barbers for that service.
        4. Then ask for a preferred date/time.
        5. Finally, ask for their name and phone number (if not provided).
        
        You have internal tools to check and update appointments!
        If a user asks "מתי התור שלי?" (When is my appointment?), ask for their phone number.
        Once you have their phone number, output an action in your JSON to check the DB.
        If a user asks to change the date/time of an existing appointment, use the update action.
        
        CRITICAL: Your output MUST be ONLY valid JSON matching this structure:
        {
           "reply": "Your response text in Hebrew",
           "options": ["Option 1", "Option 2"],
           "action": {"name": "none"}
        }
        
        To check an appointment, set action:
        "action": {"name": "check_appointments", "phone": "0542222667"}
        
        To update an appointment, set action:
        "action": {"name": "update_appointment", "appointment_id": 12, "new_date": "2026-10-01", "new_time": "14:30"}
        
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
                return data
                
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
            else:
                action_result = json.dumps({"status": "error", "message": "Unknown action"})
                
            # Feed result back to model as a user message (system simulation)
            history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"<system_tool_result>{action_result}</system_tool_result> Please summarize this for the user in Hebrew. Tell them what changed or what you found.")]))
            
            # Recurse
            return await self._generate_with_actions(db, history, depth + 1)
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "reply": "מצטערים, המערכת החכמה שלנו חווה כרגע עומס זמני.",
                "options": []
            }
