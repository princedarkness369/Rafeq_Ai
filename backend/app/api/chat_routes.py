from typing import Optional
from fastapi import APIRouter, Form, Body
from pydantic import BaseModel
from app.services.agent_service import agent_service
from app.db.mongo_client import mongo_client

chat_router = APIRouter(prefix="/api/chat", tags=["Text Chat"])

class ChatMessageRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    lang: Optional[str] = "ar"

@chat_router.post("")
async def text_chat_endpoint(payload: ChatMessageRequest = Body(...)):
    """
    POST /api/chat:
    Pure Text-Based RAG Endpoint.
    Grounded strictly in scraped University of Jordan knowledge with clickable citations.
    """
    result = agent_service.process_student_query(
        prompt=payload.prompt,
        session_id=payload.session_id,
        lang=payload.lang or "ar"
    )

    return {
        "session_id": result["session_id"],
        "answer": result["answer"],
        "cards": result.get("cards", []),
        "citations": result.get("citations", []),
        "fallback_used": result.get("fallback_used", False),
        "fallback_link": result.get("fallback_link"),
        "branch": result.get("branch")
    }

@chat_router.get("/history/{session_id}")
def get_session_history_endpoint(session_id: str):
    """GET /api/chat/history/{session_id}: Retrieve chat session history from MongoDB."""
    session = mongo_client.get_chat_session(session_id)
    if not session:
        return {"session_id": session_id, "history": []}
    return session
