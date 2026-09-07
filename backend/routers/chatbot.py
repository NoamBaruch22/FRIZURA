from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.chatbot_service import ChatbotService
from backend.main import limiter
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])
chatbot = ChatbotService()

class ChatMessage(BaseModel):
    role: str
    content: str
    options: List[str] = []

class ChatRequest(BaseModel):
    phone: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str
    options: List[str] = []

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_req: ChatRequest, db: AsyncSession = Depends(get_db)):
    data = await chatbot.process_chat(db, chat_req.phone, chat_req.messages)
    return {"reply": data["reply"], "options": data.get("options", [])}
