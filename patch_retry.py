import re

with open('backend/services/chatbot_service.py', 'r') as f:
    code = f.read()

# I need to wrap the generate_content call in a retry loop.
old_try = """        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)"""

new_try = """        try:
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
                    
            data = json.loads(response.text)"""

if old_try in code:
    code = code.replace(old_try, new_try)
    with open('backend/services/chatbot_service.py', 'w') as f:
        f.write(code)
    print("Retry logic added.")
else:
    print("Could not find the try block!")
