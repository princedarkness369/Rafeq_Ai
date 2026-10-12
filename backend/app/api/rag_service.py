import os
import uuid
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.db import db_service
from app.services.vector_service import vector_service

try:
    from google import genai  # type: ignore
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

SYSTEM_PROMPT = """
You are "Rafeq" (رفيق), the official academic AI guide for the University of Jordan - Aqaba Branch (aqaba.ju.edu.jo).

## Grounding & Source Rules:
- You answer STRICTLY based on the official University of Jordan Aqaba portal pages provided in `retrieved_context`.
- Ground all facts, dates, names, deans, and procedures strictly on official website sources.
- Never invent unverified dates, fake names, or false claims.
- If specific details are not found in `retrieved_context`, state clearly and concisely that they can be checked directly on the official portal (aqaba.ju.edu.jo).

## Persona & Formatting:
- Speak directly to university students (18+ years old) in realistic, concise, and friendly Arabic ("عربية ميسرة وحيوية تليق بطلبة الجامعة").
- Maximum 2 to 3 short bulleted points. No long introductions or repetitive fluff.
- If exact dates or deadlines exist in the retrieved context, highlight them prominently at the top with emojis (📅).
- ABSOLUTELY NO raw system text, NO curly braces or variable names, NO JSON code blocks, and NO robotic templates under any circumstances.

---
language: {language}
question: {question}

retrieved_context:
---
{context}
---

Now output ONLY the final concise, website-grounded Arabic response for the student.
"""

class RAGService:
    """
    Scraped-Knowledge RAG Service with Intelligent Gemini Reasoning.
    The primary source of truth is live scraped content from UJ & UJ Aqaba portals,
    supplemented by Gemini academic reasoning.
    """

    def __init__(self):
        self.client = None
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[RAGService Gemini Warning]: {e}")

    def generate_gemini_answer(
        self,
        query: str,
        retrieved_context: str,
        citations: List[Dict[str, str]],
        history: List[Dict[str, Any]],
        language: str = "ar"
    ) -> str:
        if not self.client:
            return ""

        full_prompt = SYSTEM_PROMPT.format(
            language="ar" if language == "ar" else "en",
            question=query,
            context=retrieved_context if retrieved_context.strip() else "(No specific vector context matched)"
        )

        models_to_try = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[RAGService Gemini Error - Model {model_name}]: {e}")

        return ""

    def answer_query(
        self,
        message: str,
        session_id: Optional[str] = None,
        language: str = "ar"
    ) -> Dict[str, Any]:
        """Process student query using scraped vector store documents and Gemini reasoning."""
        if not session_id:
            session_id = str(uuid.uuid4())

        # Retrieve chat history from MongoDB
        session_record = db_service.get_chat_history(session_id)
        history = session_record.get("messages", []) if session_record else []

        # 1. Similarity Search in ChromaDB (scraped pages)
        vector_results = vector_service.similarity_search(message, top_k=5)

        retrieved_texts = []
        sources = []
        seen_urls = set()
        primary_source_url = None

        for match in vector_results:
            retrieved_texts.append(match["text"])
            meta = match.get("metadata", {})
            url = meta.get("url") or meta.get("source_url")
            title = meta.get("title") or "موقع الجامعة الأردنية - فرع العقبة"
            if url and url not in seen_urls:
                if not primary_source_url:
                    primary_source_url = url
                seen_urls.add(url)
                sources.append({"title": title, "url": url})

        context_str = "\n---\n".join(retrieved_texts)

        # 2. Prompt Gemini 1.5 Flash with reasoning system prompt
        reply_text = self.generate_gemini_answer(
            query=message,
            retrieved_context=context_str,
            citations=sources,
            history=history,
            language=language
        )

        # Fallback only if Gemini API is unreachable
        if not reply_text:
            if language == "ar":
                reply_text = "أهلاً بك! يمكنك الاطلاع على كافة التفاصيل والإجراءات الخاصة بالسؤال عبر البوابة الرسمية للجامعة الأردنية - فرع العقبة (aqaba.ju.edu.jo)."
            else:
                reply_text = "Welcome! You can find further details and procedures on the official University of Jordan Aqaba portal (aqaba.ju.edu.jo)."

        # Save conversation history in MongoDB
        db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
        db_service.save_chat_message(session_id, role="assistant", content=reply_text, student_language=language)

        return {
            "reply": reply_text,
            "answer": reply_text,
            "source_url": primary_source_url or settings.UNIVERSITY_BASE_URL,
            "sources": sources,
            "session_id": session_id
        }

rag_service = RAGService()
