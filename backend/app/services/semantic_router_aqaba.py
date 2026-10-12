from typing import Dict, Any, Optional
from app.services.agent_service import agent_service

def process_aqaba_student_guide(
    prompt: str,
    session_id: Optional[str] = None,
    lang: str = "ar"
) -> Dict[str, Any]:
    """Delegate student guide queries to the RAG Agent Service."""
    return agent_service.process_student_query(prompt, session_id=session_id, lang=lang)

def process_aqaba_query(
    prompt: str,
    session_id: Optional[str] = None,
    lang: str = "ar"
) -> Dict[str, Any]:
    return process_aqaba_student_guide(prompt, session_id=session_id, lang=lang)
