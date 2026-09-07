import os
import json
from google import genai
from google.genai import types
from backend.config import settings

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
        6. When asking a question with a predefined set of answers (e.g., Which barber? Men/Women? Service type?), you MUST provide those answers in the `options` array.
        7. When asking for open-ended info (Name, Phone), the `options` array MUST be empty.
        
        CRITICAL: Your output MUST be ONLY valid JSON matching this structure:
        {
           "reply": "Your response text in Hebrew",
           "options": ["Option 1", "Option 2"]
        }
        Do not wrap the JSON in Markdown code blocks like ```json.
        """

    async def process_chat(self, phone: str, messages: list):
        history = []
        for m in messages:
            # Reconstruct JSON string for model history so it understands context format
            if m.role == "user":
                history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"<user_input>{m.content}</user_input>")]))
            else:
                # Mock the model's past responses as JSON strings too
                history.append(types.Content(role="model", parts=[types.Part.from_text(text=json.dumps({"reply": m.content, "options": m.options if hasattr(m, 'options') else []}, ensure_ascii=False))]))
                
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
            # The response is guaranteed to be a JSON string thanks to response_mime_type
            data = json.loads(response.text)
            return data
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "reply": "מצטערים, המערכת החכמה שלנו חווה כרגע עומס זמני או שגיאת התחברות לשרתי Google. אנא נסה שנית בעוד כמה דקות.",
                "options": []
            }
