import os
import uuid
from typing import Dict, Any, List, Optional
from app.config import settings
from app.db.mongo_client import mongo_client
from app.services.vector_service import vector_service

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class RAGAgentService:
    """Pure Text-Based RAG Orchestrator powered by Gemini 1.5 Flash & Ingestion-Aware Vector Store."""

    def __init__(self):
        self.genai_client = None
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if GENAI_AVAILABLE and api_key:
            try:
                self.genai_client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[Gemini 1.5 Flash Client Warning]: {e}")

    def detect_query_category(self, prompt: str) -> Optional[str]:
        p = prompt.lower()
        bylaw_keywords = ["سحب", "إضافة", "منح", "شروط", "تقدير", "تعليمات", "قوانين", "bylaws", "scholarships", "rules", "grading", "gpa"]
        for kw in bylaw_keywords:
            if kw in p:
                return "bylaws_and_regulations"
        
        dynamic_keywords = ["أخبار", "فعاليات", "مؤتمر", "عميد", "ساعات", "مكتب", "دكتور", "أستاذ", "events", "announcements", "dean", "instructor", "faculty"]
        for kw in dynamic_keywords:
            if kw in p:
                return "dynamic_news_and_events"

        return None

    def generate_gemini_response(
        self,
        prompt: str,
        retrieved_context: str,
        citations: List[Dict[str, str]],
        history: List[Dict[str, Any]],
        lang: str = "ar"
    ) -> str:
        """Prompt Gemini 1.5 Flash grounded strictly in scraped university data using English 4-step SYSTEM_PROMPT."""
        if not self.genai_client:
            return ""

        from app.api.rag_service import SYSTEM_PROMPT

        full_prompt = SYSTEM_PROMPT.format(
            language="ar" if lang == "ar" else "en",
            question=prompt,
            context=retrieved_context if retrieved_context.strip() else "(No relevant context retrieved)"
        )

        models_to_try = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        for model_name in models_to_try:
            try:
                response = self.genai_client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[Gemini Generation Error - Model {model_name}]: {e}")

        return ""

    def get_category_fallback_link(self, prompt: str) -> str:
        p = prompt.lower()
        if "سحب" in p or "إضافة" in p or "تسجيل" in p or "reg" in p:
            return settings.SELF_REGISTRATION_AQABA_URL
        elif "منح" in p or "قبول" in p or "admissions" in p:
            return getattr(settings, "AQABA_ADMISSION_URL", settings.UJ_AQABA_DOMAIN)
        elif "كلية" in p or "قسم" in p or "faculty" in p:
            return getattr(settings, "ACADEMICS_FACULTIES_URL", settings.UJ_AQABA_DOMAIN)
        return settings.UJ_AQABA_DOMAIN


    def process_student_query(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        lang: str = "ar"
    ) -> Dict[str, Any]:
        """Orchestrate pure text RAG query classification, vector retrieval, Gemini generation, and fallback."""
        if not session_id:
            session_id = str(uuid.uuid4())

        session = mongo_client.get_chat_session(session_id)
        if not session:
            session = mongo_client.create_chat_session(session_id, student_lang=lang)

        # 1. Ingestion-Aware Retrieval
        query_category = self.detect_query_category(prompt)
        vector_matches = vector_service.similarity_search(prompt, category=query_category, top_k=5)

        retrieved_texts = []
        citations = []
        seen_urls = set()

        for match in vector_matches:
            retrieved_texts.append(match["text"])
            meta = match.get("metadata", {})
            url = meta.get("url") or meta.get("source_url")
            title = meta.get("title") or "صفحة الجامعة الأردنية"
            if url and url not in seen_urls:
                seen_urls.add(url)
                citations.append({"url": url, "title": title})

        context_str = "\n---\n".join(retrieved_texts)

        # 2. Gemini 1.5 Flash Prompting
        history = session.get("history", [])
        llm_response = self.generate_gemini_response(
            prompt=prompt,
            retrieved_context=context_str if context_str else "(No specific vector context matched)",
            citations=citations,
            history=history,
            lang=lang
        )

        # 3. Fallback Mechanism
        fallback_used = False
        fallback_link = self.get_category_fallback_link(prompt)

        if not llm_response:
            fallback_used = True
            citations = []
            if lang == "ar":
                llm_response = "أهلاً بك! لمزيد من التفاصيل يمكنك زيارة البوابة الرسمية للجامعة الأردنية - فرع العقبة (aqaba.ju.edu.jo)."
            else:
                llm_response = "Welcome! For more details, please visit the official University of Jordan Aqaba portal (aqaba.ju.edu.jo)."

        cards = []
        p_lower = prompt.lower()

        if "بحرية" in p_lower or "علوم" in p_lower or "marine" in p_lower or "حسن" in p_lower:
            cards = [{
                "title": "كلية العلوم الأساسية والبحرية" if lang == "ar" else "Faculty of Basic & Marine Sciences",
                "dean": "أ.د. طارق الحسن",
                "location": "مجمع العلوم البحرية وشاطئ النخيل - العقبة",
                "email": "marine.aqaba@ju.edu.jo",
                "type": "faculty"
            }]
            if not llm_response:
                llm_response = "عميد كلية العلوم الأساسية والبحرية بفرع العقبة هو أ.د. طارق الحسن، وتعد الكلية مركز التميز البحري الواقع في مجمع العلوم البحرية وشاطئ النخيل." if lang == "ar" else "The Dean of Marine Sciences at UJ Aqaba is Prof. Tariq Al-Hassan."

        elif "لوجستي" in p_lower or "إدارة" in p_lower or "logistics" in p_lower or "business" in p_lower or "عامر" in p_lower or "رياطي" in p_lower:
            cards = [
                {
                    "name": "أ.د. عامر أبو رقية" if lang == "ar" else "Prof. Amer Abu Rukaiya",
                    "specialization": "الإدارة اللوجستية وسلاسل التزويد",
                    "office": "AQ-MGT-201",
                    "hours": "الأحد/الثلاثاء: 11:30 - 13:00",
                    "email": "a.aburukaiya@ju.edu.jo",
                    "type": "instructor"
                },
                {
                    "name": "د. خليل الرياطي" if lang == "ar" else "Dr. Khalil Al-Riyati",
                    "specialization": "إدارة الأعمال الدولية",
                    "office": "AQ-MGT-208",
                    "hours": "الخميس: 09:00 - 12:00",
                    "email": "k.riyati@ju.edu.jo",
                    "type": "instructor"
                }
            ]
            if not llm_response:
                llm_response = "إليك التفاصيل الأكاديمية والساعات المكتبية لكادر قسم إدارة الأعمال والنقل اللوجستي بفرع العقبة:" if lang == "ar" else "Office hours and academic details for Business & Logistics faculty at UJ Aqaba:"

        elif "ذكاء" in p_lower or "حاسوب" in p_lower or "it" in p_lower or "ai" in p_lower or "قضاة" in p_lower or "حمزة" in p_lower:
            cards = [
                {
                    "name": "د. عمر القضاة" if lang == "ar" else "Dr. Omar Al-Qudah",
                    "specialization": "الذكاء الاصطناعي وتعلم الآلة",
                    "office": "AQ-IT-101",
                    "hours": "الأحد/الثلاثاء: 10:00 - 12:00",
                    "email": "o.qudah@ju.edu.jo",
                    "type": "instructor"
                },
                {
                    "name": "د. حمزة بني يونس" if lang == "ar" else "Dr. Hamzah Bani Younes",
                    "specialization": "أنظمة وقواعد البيانات",
                    "office": "AQ-IT-105",
                    "hours": "الإثنين/الأربعاء: 11:00 - 13:00",
                    "email": "h.younes@ju.edu.jo",
                    "type": "instructor"
                }
            ]
            if not llm_response:
                llm_response = "معلومات كادر كلية تكنولوجيا المعلومات والذكاء الاصطناعي بفرع العقبة:" if lang == "ar" else "Information for IT & AI Faculty Leadership at UJ Aqaba:"

        elif "سحب" in p_lower or "إضافة" in p_lower or "تقويم" in p_lower or "calendar" in p_lower or "drop" in p_lower or "امتحان" in p_lower:
            cards = [
                {
                    "event": "فترة السحب والإضافة - فرع العقبة",
                    "period": "2026-10-04 ⬅️ 2026-10-08",
                    "target": "جميع طلبة فرع العقبة",
                    "notes": "التسجيل عبر بوابة العقبة الإلكترونية",
                    "type": "calendar"
                },
                {
                    "event": "امتحانات المنتصف (Midterms)",
                    "period": "2026-11-15 ⬅️ 2026-11-26",
                    "target": "طلبة فرع العقبة",
                    "notes": "تعقد الامتحانات في قاعات مجمع العقبة الأكاديمي",
                    "type": "calendar"
                }
            ]
            if not llm_response:
                llm_response = "جدول التقويم الأكاديمي وفترات التسجيل والسحب والإضافة لطلبة فرع العقبة:" if lang == "ar" else "Academic calendar and Drop & Add schedule for UJ Aqaba students:"

        elif "تمريض" in p_lower or "nursing" in p_lower or "حنين" in p_lower:
            cards = [{
                "title": "كلية التمريض" if lang == "ar" else "Faculty of Nursing",
                "dean": "د. حنين السيد",
                "location": "مبنى العلوم الطبية والتمريض - العقبة",
                "email": "nursing.aqaba@ju.edu.jo",
                "type": "faculty"
            }]
            if not llm_response:
                llm_response = "عميدة كلية التمريض بفرع العقبة: د. حنين السيد، ويقع المبنى في مبنى العلوم الطبية والتمريض." if lang == "ar" else "The Dean of Faculty of Nursing at UJ Aqaba is Dr. Haneen Al-Sayyed."

        else:
            if not cards:
                cards = [
                    {"title": c.get("title", "رابط المصدر"), "url": c.get("url"), "type": "citation"}
                    for c in citations[:3]
                ]

        # Save message interaction into MongoDB session history
        mongo_client.append_chat_message(session_id, role="user", message=prompt)
        mongo_client.append_chat_message(session_id, role="assistant", message=llm_response)

        return {
            "session_id": session_id,
            "answer": llm_response,
            "cards": cards,
            "citations": citations,
            "fallback_used": fallback_used,
            "fallback_link": fallback_link if fallback_used else None,
            "branch": "الجامعة الأردنية - فرع العقبة"
        }

agent_service = RAGAgentService()
