import sys
import os
import uuid
from typing import Dict, Any, List, Optional, Tuple
from app.config import settings
from app.services.db import db_service
from app.services.vector_service import vector_service

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    types = None

SYSTEM_PROMPT = """# Role & Identity
You are "Rafeeq" (رفيق), the official academic and institutional AI assistant for the University of Jordan - Aqaba Branch (الجامعة الأردنية - فرع العقبة). Your primary purpose is to assist students, prospective applicants, and visitors with accurate information regarding the university, its faculties, academic programs, campus facilities, student services, and academic guidelines.

---
# Core Operating Rules

1. **Full Contextual Understanding (No Isolated Keyword Matching):**
   - Strictly prohibit relying on isolated keywords or standalone words (e.g., picking up a word like "Jordan" or "University" detached from the rest of the sentence).
   - Before generating any response, analyze the entire sentence to understand the complete user intent, context, and core subject matter.

2. **No Conversational Baiting in Greetings:**
   - When greeted (e.g. "كيفك", "مرحبا", "سلام", "صباح الخير", "مساء الخير", "hello", "hi"):
     Respond politely, concisely, and formally as an institutional academic advisor WITHOUT asking personal follow-up questions like "طمني عنك" or "كيف دراستك".
     Directly ask how you can assist with official University of Jordan - Aqaba Branch inquiries.
     * Arabic response: "أهلاً بك! أنا رفيق، مرشدك الأكاديمي في الجامعة الأردنية فرع العقبة. كيف يمكنني مساعدتك في استفساراتك الأكاديمية أو الإدارية اليوم؟"
     * English response: "Hello! I am Rafeeq, your academic assistant for the University of Jordan (Aqaba Branch). How can I assist you with your university inquiries today?"

3. **Handling Personal Statements & Life Updates (No Database Record Searches):**
   - When the user shares personal updates, feelings, or exam stress (e.g. "بكره علي امتحان", "درست كثير اليوم", "تعبان", "حاس بضغط", "نعسان", "خايف من الامتحان", "I have an exam tomorrow", "I am tired"):
     NEVER search university records and NEVER output "بحثت في السجلات الحالية لفرع العقبة ولم أجد تاريخاً/اسماً معلناً...".
     Instead, reply briefly wishing them success, state that your role is strictly limited to answering official university, academic, and administrative questions (majors, registration, schedules, facilities), and ask if they have a specific university inquiry.
     * Arabic response: "أتمنى لك كل التوفيق والنجاح! يقتصر دوري كمساعد أكاديمي رسمي على الإجابة عن استفسارات الجامعة الأردنية فرع العقبة الرسمية والأنظمة ومواعيد التسجيل ومرافق الكليات. هل لديك استفسار محدد بخصوص المواد أو الجداول أو معاملات الجامعة لمساعدتك به؟"
     * English response: "I wish you all the best and great success! My role is strictly dedicated to answering official inquiries regarding the University of Jordan (Aqaba Branch), including academic regulations, registration dates, majors, and campus facilities. Do you have a specific university inquiry I can assist you with?"

4. **Scope Classification & Out-of-Scope Redirection:**
   - **In-Scope:** Inquiries directly related to the University of Jordan - Aqaba Branch, its colleges, majors, faculty members, schedules, admission, registration, campus facilities, and student activities.
   - **Out-of-Scope / Edge Cases:** General knowledge questions (geographical, political, etc.), unexpected test prompts (e.g., asking "Are you from Jordan?", "ما هي عاصمة الأردن؟", or trying to trick the model with isolated terms).
   - If a question falls outside the university's scope or is an unexpected test prompt, your response MUST politely redirect the user back to university-related topics using this exact formulation:
     * In Arabic:
       "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!"
     * In English:
       "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch). I would be more than happy to help you with any questions related to university majors, facilities, or student services!"

5. **Tone & Style:**
   - Be precise, friendly, helpful, and professional as an institutional university assistant.
   - Respond in clear, smooth Modern Standard Arabic by default (or English if the user is communicating in English).
   - Do NOT mix English acronyms inside parentheses in Arabic labels (e.g. use "بوابة التسجيل الذاتي للطلبة", "منصة التعلم الإلكتروني", "كلية تكنولوجيا المعلومات").

---
# Institutional Knowledge & Verified Data (University of Jordan - Aqaba Branch)

1. **Direct Answers (No Evasion):**
   - Provide direct facts, names, dates, and locations immediately based on verified university records or live Google Search Grounding across `aqaba.ju.edu.jo` and `ju.edu.jo`.

2. **Colleges, Deans & Faculty Directory:**
   - **كلية تكنولوجيا المعلومات (نظم وتكنولوجيا المعلومات):** العميد **الدكتور سفيان الغزيوات**
   - **كلية إدارة الأعمال (الإدارة والتمويل):** العميد **الدكتور عمر سنجلاوي**
   - **كلية السياحة والفندقة:** العميد **الدكتور عمر جوابرة**
   - **كلية التمريض:** العميد **الدكتور محمود الكلالدة**
   - **كلية الأحياء (العلوم الأساسية والبحرية):** العميد **الدكتور محمود الكلالدة**
   - **كلية الرياضيات (العلوم الأساسية):** العميد **الدكتور محمود الكلالدة**
   - **كلية اللغات:** عمادة كلية اللغات
   - **أعضاء الهيئة التدريسية:** https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx
   - نائب رئيس الجامعة لشؤون فرع العقبة: الأستاذ الدكتور غالب عباسي.
   - ساعات الدوام الرسمي: الأحد إلى الخميس، من 8:00 صباحاً وحتى 3:00 عصراً (مبنى الإدارة والقبول والتسجيل الرئيسي، المحدود الشمالي).

3. **Academic Calendar 2026/2027 (التقويم الجامعي المعتمد):**
   - **فترة السحب والإضافة:** الأحد 4-10-2026 حتى الخميس 8-10-2026
   - **بدء التدريس للفصل الأول:** الأحد 11-10-2026
   - **امتحانات منتصف الفصل الدراسي:** الأحد 29-11-2026 حتى الخميس 10-12-2026
   - **فترة التسجيل على مواد الفصل الثاني:** الأحد 13-12-2026 حتى الخميس 24-12-2026
   - **عطلة عيد الميلاد المجيد:** الجمعة 25-12-2026
   - **عطلة رأس السنة الميلادية:** الجمعة 1-1-2027
   - **فترة تقديم طلبات الانتقال من تخصص لآخر إلكترونياً:** الأحد 3-1-2027 حتى الأربعاء 3-2-2027
   - **آخر يوم للتدريس في الفصل الأول:** الأربعاء 13-1-2027
   - **آخر موعد للانسحاب من دراسة المواد:** الخميس 14-1-2027
   - **الامتحانات النهائية للفصل الأول:** الأحد 17-1-2027 حتى الخميس 28-1-2027
   - **إجازة ما بين الفصلين للطلبة:** الأحد 31-1-2027 حتى الخميس 11-2-2027

4. **Whitelisted Official Portals:**
   - موقع فرع العقبة الرسمي: https://aqaba.ju.edu.jo
   - بوابة التسجيل الذاتي للطلبة: https://ujapps.ju.edu.jo/selfregappaq/
   - منصة التعلم الإلكتروني: https://elearning.ju.edu.jo
   - وحدة القبول والتسجيل: https://registration.ju.edu.jo
   - نظام تقديم الشكاوى والاقتراحات: https://eservices.ju.edu.jo/complaintsys/login.aspx
   - دليل الكليات وأعضاء الهيئة التدريسية: https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx
   - موقع الجامعة الأم (عمّان): https://www.ju.edu.jo

---
language: {language}
question: {question}

retrieved_context:
---
{context}
---

الآن حلل السؤال وفحواه بالكامل وقدم إجابتك الاحترافية الموثقة:
"""

class RAGService:
    """
    Scraped-Knowledge RAG Service with Intelligent Gemini Reasoning.
    The primary source of truth is live scraped content from UJ & UJ Aqaba portals,
    supplemented by Gemini academic reasoning, Google Search grounding, and Base Knowledge.
    """

    def __init__(self):
        self.client = self._init_client()

    def _init_client(self):
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            print("[RAGService Alert] GEMINI_API_KEY is not set in backend/.env!")
            return None

        if not GENAI_AVAILABLE:
            print("[RAGService Alert] google-genai library is not installed or import failed!")
            return None

        # 1. Support Vertex AI Express Mode for keys starting with 'AQ.'
        if api_key.startswith("AQ."):
            try:
                print("[RAGService] Detected 'AQ.' key prefix: Initializing Gemini Client with vertexai=True (Vertex AI Express Mode)...")
                client = genai.Client(vertexai=True, api_key=api_key)
                print("[RAGService] Google Gemini Vertex AI Client successfully initialized.")
                return client
            except Exception as e:
                print(f"[RAGService Notice] Vertex AI mode init warning: {e}")

        # 2. Standard Google AI Studio mode (for AIzaSy... or standard API keys)
        try:
            print("[RAGService] Initializing Gemini Client with Google AI Studio mode...")
            client = genai.Client(api_key=api_key)
            print("[RAGService] Google Gemini Client successfully initialized.")
            return client
        except Exception as e:
            print(f"[RAGService Error] Failed to initialize Gemini Client: {e}")
            return None

    def _get_search_config(self):
        """Construct configuration with Google Search Grounding enabled."""
        if not types:
            return {"tools": [{"google_search": {}}]}
        try:
            return types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.3
            )
        except Exception:
            try:
                return types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.3
                )
            except Exception:
                return {"tools": [{"google_search": {}}]}

    def _get_institutional_base_answer(self, query: str, language: str = "ar") -> Tuple[Optional[str], Optional[str]]:
        """
        Provides immediate factual responses and official portal citations for verified institutional queries.
        Returns a tuple: (answer_text, source_url)
        """
        q = query.lower()
        q_norm = q.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

        # 1. Deans of UJ Aqaba Colleges
        # IT Dean
        if any(w in q_norm for w in ["سفيان", "غزيوات"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["تكنولوجيا", "it", "نظم", "حاسوب", "معلومات", "اي تي"])):
            if language == "en":
                ans = "Dean of the Faculty of Information Technology at the University of Jordan - Aqaba Branch is **Dr. Sufyan Al-Ghazaiwat**."
            else:
                ans = "أهلاً بك! عميد كلية تكنولوجيا المعلومات (نظم وتكنولوجيا المعلومات) في الجامعة الأردنية فرع العقبة هو **الدكتور سفيان الغزيوات**."
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # Business Dean
        if any(w in q_norm for w in ["سنجلاوي", "عمر سنجلاوي"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["اداره", "اعمال", "الاعمال", "تمويل", "بزنس", "business"])):
            if language == "en":
                ans = "Dean of the Faculty of Business (Management & Finance) at the University of Jordan - Aqaba Branch is **Dr. Omar Sinjilawi**."
            else:
                ans = "أهلاً بك! عميد كلية إدارة الأعمال (الإدارة والتمويل) في الجامعة الأردنية فرع العقبة هو **الدكتور عمر سنجلاوي**."
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # Tourism Dean
        if any(w in q_norm for w in ["جوابره", "عمر جوابره"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["سياحه", "فندقه", "سياحة", "tourism"])):
            if language == "en":
                ans = "Dean of the Faculty of Tourism & Hospitality at the University of Jordan - Aqaba Branch is **Dr. Omar Jawbrah**."
            else:
                ans = "أهلاً بك! عميد كلية السياحة والفندقة في الجامعة الأردنية فرع العقبة هو **الدكتور عمر جوابرة**."
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # Nursing, Biology, Math
        if any(w in q_norm for w in ["كلالده", "محمود الكلالده"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["تمريض", "التمريض", "احياء", "الاحياء", "رياضيات", "الرياضيات", "علوم بحريه", "علوم اساسيه"])):
            if language == "en":
                ans = "Dean of the Faculty of Nursing, Faculty of Biology, and Faculty of Mathematics (Basic & Marine Sciences) at the University of Jordan - Aqaba Branch is **Dr. Mahmoud Al-Kalaldah**."
            else:
                ans = "أهلاً بك! عميد كلية التمريض، وكلية الأحياء، وكلية الرياضيات (العلوم الأساسية والبحرية) في فرع العقبة هو **الدكتور محمود الكلالدة**."
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # General Deans Question
        if any(w in q_norm for w in ["عمداء الكليات", "مين هم العمداء", "اسماء العمداء", "من هم العمداء", "عمداء كليات", "who are the deans", "list of deans"]):
            if language == "en":
                ans = (
                    "Here is the official list of Faculty Deans at the University of Jordan - Aqaba Branch:\n"
                    "• **Faculty of Information Technology:** Dr. Sufyan Al-Ghazaiwat\n"
                    "• **Faculty of Business:** Dr. Omar Sinjilawi\n"
                    "• **Faculty of Tourism & Hospitality:** Dr. Omar Jawbrah\n"
                    "• **Faculty of Nursing:** Dr. Mahmoud Al-Kalaldah\n"
                    "• **Faculty of Biology:** Dr. Mahmoud Al-Kalaldah\n"
                    "• **Faculty of Mathematics:** Dr. Mahmoud Al-Kalaldah"
                )
            else:
                ans = (
                    "إليك قائمة عمداء كليات الجامعة الأردنية فرع العقبة المعتمدين:\n"
                    "• **كلية تكنولوجيا المعلومات:** الدكتور سفيان الغزيوات\n"
                    "• **كلية إدارة الأعمال:** الدكتور عمر سنجلاوي\n"
                    "• **كلية السياحة والفندقة:** الدكتور عمر جوابرة\n"
                    "• **كلية التمريض:** الدكتور محمود الكلالدة\n"
                    "• **كلية الأحياء:** الدكتور محمود الكلالدة\n"
                    "• **كلية الرياضيات:** الدكتور محمود الكلالدة"
                )
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # Faculty & Academic Staff
        if any(w in q_norm for w in ["الهيئه التدريسيه", "هيئه تدريسيه", "تدريسيه", "الهيئة التدريسية", "هيئة تدريسية", "مدرسين", "دكاتره", "اساتذه", "كادر التدريس", "faculty", "academics"]):
            if language == "en":
                ans = "You can view the full directory of faculty members, profiles, and academic departments directly via the official Academic Affairs directory."
            else:
                ans = "أهلاً بك! يمكنك التعرف على أعضاء الهيئة التدريسية وكادر التدريس لكافة كليات وأقسام فرع العقبة ومؤهلاتهم الأكاديمية مباشرة عبر صفحة الشؤون الأكاديمية الرسمية."
            return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

        # 2. Self-Registration Portal
        if any(w in q_norm for w in ["بوابه التسجيل", "تسجيل ذاتي", "التسجيل الذاتي", "سيلف ريج", "selfreg", "self registration"]):
            if language == "en":
                ans = "The official student self-registration portal for the University of Jordan - Aqaba Branch is accessible here: https://ujapps.ju.edu.jo/selfregappaq/"
            else:
                ans = "رابط بوابة التسجيل الذاتي للطلبة في الجامعة الأردنية فرع العقبة لتثبيت المواد وتعديل الجداول هو: https://ujapps.ju.edu.jo/selfregappaq/"
            return ans, "https://ujapps.ju.edu.jo/selfregappaq/"

        # 3. Complaints & Suggestions
        if any(w in q_norm for w in ["شكوى", "شكاوى", "اقتراح", "اقتراحات", "تظلم", "complaints", "suggestions"]):
            if language == "en":
                ans = "You can submit electronic complaints and suggestions via the official University portal: https://eservices.ju.edu.jo/complaintsys/login.aspx or in person at the Deanship of Student Affairs."
            else:
                ans = "يمكنك تقديم الشكاوى والاقتراحات إلكترونياً عبر قسم خدمة الجمهور والشكاوى في بوابة الجامعة الرسمية: https://eservices.ju.edu.jo/complaintsys/login.aspx أو عبر مراجعة عمادة شؤون الطلبة في الحرم الجامعي."
            return ans, "https://eservices.ju.edu.jo/complaintsys/login.aspx"

        # 4. Working Hours
        if any(w in q for w in ["دوام", "ساعات", "أوقات", "وقت", "متى يفتح", "متى يسكر", "hours", "timing", "ساعة"]):
            if language == "en":
                ans = "Official working and advising hours for all academic and administrative offices at the University of Jordan - Aqaba Branch are **Sunday to Thursday, 8:00 AM – 3:00 PM** (Friday and Saturday are official weekends)."
            else:
                ans = "ساعات الدوام الرسمي والمراجعة لكافة الدوائر الأكاديمية والإدارية ومكتب القبول والتسجيل في الجامعة الأردنية فرع العقبة هي من **الأحد إلى الخميس، من الساعة 8:00 صباحاً وحتى الساعة 3:00 عصراً**. (يومي الجمعة والسبت عطلة أسبوعية رسمية)."
            return ans, "https://registration.ju.edu.jo"

        # 5. Admission & Registration Location
        if any(w in q for w in ["مكان", "أين يقع", "وين", "موقع", "مبنى التسجيل", "مكتب القبول", "مكتب التسجيل", "admission location", "اين يقع"]):
            if language == "en":
                ans = "The Admission & Registration Directorate is located in the **Main Administration and Registration Building, inside the University of Jordan - Aqaba Campus (Northern Mahdood / University Street)**."
            else:
                ans = "يقع مكتب ووحدة القبول والتسجيل في **مبنى الإدارة والقبول والتسجيل الرئيسي داخل حرم الجامعة الأردنية فرع العقبة (منطقة المحدود الشمالي / شارع الجامعة)**، وساعات المراجعة واستقبال الطلبة من الأحد إلى الخميس من 8:00 صباحاً حتى 3:00 عصراً."
            return ans, "https://registration.ju.edu.jo"

        # 6. Add/Drop & Registration
        if any(w in q_norm for w in ["سحب", "اضافه", "السحب", "الاضافه", "موعد السحب", "متى السحب", "drop", "add"]):
            if language == "en":
                ans = "The **Add/Drop period** for the First Semester 2026/2027 runs from **Sunday, October 4, 2026 until Thursday, October 8, 2026** via the student self-registration portal."
            else:
                ans = "فترة **السحب والإضافة** للفصل الأول 2026/2027 تبدأ من يوم **الأحد 4-10-2026** وتستمر لغاية يوم **الخميس 8-10-2026** عبر بوابة التسجيل الذاتي للطلبة."
            return ans, "https://ujapps.ju.edu.jo/selfregappaq/"

        # 7. Midterm Exams
        if any(w in q_norm for w in ["منتصف الفصل", "الميد", "ميد", "امتحان نص الفصل", "امتحانات منتصف", "midterm"]):
            if language == "en":
                ans = "📅 **Midterm Exams** for the First Semester 2026/2027 begin on **Sunday, November 29, 2026** and conclude on **Thursday, December 10, 2026**."
            else:
                ans = "📅 **امتحانات منتصف الفصل الدراسي الأول** للعام الجامعي 2026/2027 تبدأ من يوم **الأحد 29-11-2026** وتستمر لغاية يوم **الخميس 10-12-2026**."
            return ans, "https://aqaba.ju.edu.jo"

        # 8. Final Exams
        if any(w in q_norm for w in ["نهائي", "نهائيه", "النهائي", "النهائيه", "فاينل", "الفاينل", "امتحانات النهائيه", "final"]):
            if language == "en":
                ans = "📅 **Final Examinations** for the First Semester 2026/2027 run from **Sunday, January 17, 2027** until **Thursday, January 28, 2027**."
            else:
                ans = "📅 **الامتحانات النهائية للفصل الأول 2026/2027** تبدأ بمشيئة الله يوم **الأحد 17-1-2027** وتستمر حتى يوم **الخميس 28-1-2027**."
            return ans, "https://aqaba.ju.edu.jo"

        # 9. Semester Break
        if any(w in q_norm for w in ["بين الفصلين", "عطله بين الفصلين", "اجازه بين الفصلين", "العطله", "semester break"]):
            if language == "en":
                ans = "🌴 **Inter-Semester Student Break** runs from **Sunday, January 31, 2027** until **Thursday, February 11, 2027**."
            else:
                ans = "🌴 **إجازة ما بين الفصلين للطلبة** تبدأ يوم **الأحد 31-1-2027** وتستمر لغاية يوم **الخميس 11-2-2027**."
            return ans, "https://aqaba.ju.edu.jo"

        # 10. General Calendar
        if any(w in q_norm for w in ["التقويم", "تقويم", "مواعيد الفصل", "تواريخ الفصل", "academic calendar", "semester schedule"]):
            if language == "en":
                ans = (
                    "Official Academic Calendar for UJ Aqaba Branch 2026/2027:\n"
                    "• Add/Drop Period: October 4, 2026 – October 8, 2026\n"
                    "• Classes Begin: October 11, 2026\n"
                    "• Midterm Exams: November 29, 2026 – December 10, 2026\n"
                    "• Second Semester Course Registration: December 13, 2026 – December 24, 2026\n"
                    "• Final Examinations: January 17, 2027 – January 28, 2027\n"
                    "• Inter-Semester Break: January 31, 2027 – February 11, 2027"
                )
            else:
                ans = (
                    "التقويم الجامعي المعتمد لفرع العقبة 2026/2027:\n"
                    "• السحب والإضافة: 4-10-2026 إلى 8-10-2026\n"
                    "• بدء التدريس: 11-10-2026\n"
                    "• امتحانات منتصف الفصل الدراسي: 29-11-2026 إلى 10-12-2026\n"
                    "• تسجيل الفصل الثاني: 13-12-2026 إلى 24-12-2026\n"
                    "• الامتحانات النهائية: 17-1-2027 إلى 28-1-2027\n"
                    "• إجازة ما بين الفصلين: 31-1-2027 إلى 11-2-2027"
                )
            return ans, "https://aqaba.ju.edu.jo"

        # 11. E-Learning
        if any(w in q_norm for w in ["مودل", "moodle", "التعلم الالكتروني", "التعليم الالكتروني", "elearning"]):
            if language == "en":
                ans = "You can access the official E-Learning platform for coursework and assessments via: https://elearning.ju.edu.jo"
            else:
                ans = "يمكنك الدخول إلى منصة التعلم الإلكتروني الرسمية لمتابعة المحاضرات والمساقات عبر الرابط: https://elearning.ju.edu.jo"
            return ans, "https://elearning.ju.edu.jo"

        # 12. Faculties
        if any(w in q_norm for w in ["كليات", "الكليات", "تخصصات", "التخصصات", "faculties", "colleges"]):
            if language == "en":
                ans = (
                    "The University of Jordan - Aqaba Branch hosts 6 accredited faculties:\n"
                    "1. Faculty of Information Technology\n"
                    "2. Faculty of Business\n"
                    "3. Faculty of Tourism & Hospitality\n"
                    "4. Faculty of Languages\n"
                    "5. Faculty of Nursing\n"
                    "6. Faculty of Basic & Marine Sciences"
                )
            else:
                ans = (
                    "تضم الجامعة الأردنية فرع العقبة 6 كليات رسمية معتمدة:\n"
                    "1. كلية تكنولوجيا المعلومات\n"
                    "2. كلية إدارة الأعمال\n"
                    "3. كلية السياحة والفندقة\n"
                    "4. كلية اللغات\n"
                    "5. كلية التمريض\n"
                    "6. كلية العلوم الأساسية والبحرية"
                )
            return ans, "https://aqaba.ju.edu.jo"

        return None, None

    def generate_gemini_answer(
        self,
        query: str,
        retrieved_context: str,
        citations: List[Dict[str, str]],
        history: List[Dict[str, Any]],
        language: str = "ar"
    ) -> str:
        if not self.client:
            self.client = self._init_client()

        if not self.client:
            print("[RAGService Alert] Gemini client unavailable; checking base institutional knowledge.")
            return ""

        full_prompt = SYSTEM_PROMPT.format(
            language="ar" if language == "ar" else "en",
            question=query,
            context=retrieved_context if retrieved_context.strip() else "(قاعدة البيانات المحلية لم ترجع مقاطع محددة، اعتمد على Base Knowledge و Google Search)"
        )

        candidate_models = []
        if settings.GEMINI_MODEL:
            candidate_models.append(settings.GEMINI_MODEL)
        candidate_models.extend([
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
        ])
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        search_config = self._get_search_config()

        for model_name in models_to_try:
            # 1. Attempt with Google Search Grounding
            try:
                print(f"[RAGService] Invoking Gemini model '{model_name}' WITH Google Search Grounding...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=search_config
                )
                if response and response.text:
                    print(f"[RAGService] Successfully generated response using '{model_name}' with Search Grounding!")
                    return response.text.strip()
            except Exception as search_err:
                err_str = str(search_err)
                print(f"[RAGService Notice] Search grounding attempt on '{model_name}' failed: {err_str[:120]}")
                if "API key not valid" in err_str or "UNAUTHENTICATED" in err_str:
                    print("[RAGService CRITICAL] Gemini API Key is invalid or unauthenticated! Get a valid key starting with 'AIzaSy' from https://aistudio.google.com/app/apikey")
                    return ""

            # 2. Retrying without search tool (Standard Mode: Base Knowledge + Context)
            try:
                print(f"[RAGService] Retrying Gemini model '{model_name}' in standard mode (Base Knowledge + Context)...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text:
                    print(f"[RAGService] Successfully generated response using '{model_name}' in standard mode!")
                    return response.text.strip()
            except Exception as standard_err:
                err_str = str(standard_err)
                print(f"[RAGService Error] Standard generation failed on '{model_name}': {err_str[:120]}")
                if "API key not valid" in err_str or "UNAUTHENTICATED" in err_str:
                    print("[RAGService CRITICAL] Gemini API Key is invalid or unauthenticated! Get a valid key starting with 'AIzaSy' from https://aistudio.google.com/app/apikey")
                    return ""

        print("[RAGService Error] All candidate models failed to return a response.")
        return ""

    def answer_query(
        self,
        message: str,
        session_id: Optional[str] = None,
        language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Process student query with strict intent classification, zero conversational baiting,
        and conditional official source links.
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        q = message.strip()
        q_norm = q.lower().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

        # Intent 1: GREETINGS (Concise, polite, NO conversational baiting, NO source link)
        greeting_words = ["مرحبا", "سلام", "اهلا", "كيفك", "شو اخبارك", "صباح الخير", "مساء الخير", "hello", "hi", "hey", "good morning", "good evening"]
        is_greeting = any(w in q_norm for w in greeting_words) and len(q_norm.split()) <= 4 and not any(k in q_norm for k in ["جامع", "كلي", "تسجيل", "عميد", "سحب", "امتحان", "دوام", "موعد", "رسمي", "رسوم", "تخصص"])
        if is_greeting:
            if language == "en":
                reply_text = "Hello! I am Rafeeq, your official academic assistant for the University of Jordan (Aqaba Branch). How can I assist you with your academic inquiries today?"
            else:
                reply_text = "أهلاً بك! أنا رفيق، مرشدك الأكاديمي في الجامعة الأردنية فرع العقبة. كيف يمكنني مساعدتك في استفساراتك الأكاديمية والجامعية اليوم؟"

            db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
            db_service.save_chat_message(session_id, role="assistant", content=reply_text, student_language=language)
            return {
                "reply": reply_text,
                "answer": reply_text,
                "source_url": None,
                "sources": [],
                "session_id": session_id
            }

        # Intent 2: PERSONAL STATEMENTS / LIFE UPDATES / EXAM STRESS (NO database search, NO record fallback, NO source link)
        personal_update_phrases = [
            "علي امتحان", "عندي امتحان", "امتحان بكره", "امتحان غدا", "درست كثير", "درست كتير", "بدرس", "تعبان", "حاس بضغط",
            "مضغوط", "مش قادر ادرس", "مش ملحق", "نعسان", "خايف من الامتحان", "راسي بوجعني", "ما نمت", "قلقان", "زهقان",
            "i have an exam", "i have test", "studied a lot", "feeling tired", "so tired", "stressed", "cant study", "sleepy"
        ]
        is_personal_statement = any(p in q_norm for p in personal_update_phrases) and not any(k in q_norm for k in ["متى", "اين", "وين", "كم", "شروط", "عميد", "سحب", "اضاف", "موعد الامتحان", "جدول الامتحانات", "when", "where", "how"])
        if is_personal_statement:
            if language == "en":
                reply_text = "I wish you all the best and great success! My role is strictly dedicated to answering official inquiries regarding the University of Jordan (Aqaba Branch), including academic regulations, registration dates, majors, and campus facilities. Do you have a specific university inquiry I can assist you with?"
            else:
                reply_text = "أتمنى لك كل التوفيق والنجاح! يقتصر دوري كمساعد أكاديمي رسمي على الإجابة عن استفسارات الجامعة الأردنية فرع العقبة الرسمية والأنظمة ومواعيد التسجيل ومرافق الكليات. هل لديك استفسار محدد بخصوص المواد أو الجداول أو معاملات الجامعة لمساعدتك به؟"

            db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
            db_service.save_chat_message(session_id, role="assistant", content=reply_text, student_language=language)
            return {
                "reply": reply_text,
                "answer": reply_text,
                "source_url": None,
                "sources": [],
                "session_id": session_id
            }

        # Intent 3: OUT-OF-SCOPE / TRICK TEST PROMPTS (NO database search, NO source link)
        out_of_scope_prompts = [
            "هل انت من الاردن", "انت من الاردن", "are you from jordan",
            "عاصمه الاردن", "عاصمة الاردن", "capital of jordan",
            "رئيس وزراء", "رئيس الحكومة", "prime minister",
            "احكيلي نكته", "احكيلي قصه", "tell me a joke", "tell me a story",
            "طقس اليوم", "الطقس في", "weather in", "عاصمه فرنسا", "capital of france"
        ]
        is_out_of_scope = any(p in q_norm for p in out_of_scope_prompts) and not any(k in q_norm for k in ["جامع", "كلي", "تسجيل", "عميد", "سحب", "امتحان", "دوام"])
        if is_out_of_scope:
            if language == "en":
                reply_text = "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch). I would be more than happy to help you with any questions related to university majors, facilities, or student services!"
            else:
                reply_text = "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!"

            db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
            db_service.save_chat_message(session_id, role="assistant", content=reply_text, student_language=language)
            return {
                "reply": reply_text,
                "answer": reply_text,
                "source_url": None,
                "sources": [],
                "session_id": session_id
            }

        # Intent 4: Check Base Knowledge First (Immediate Verified Facts with Source URL)
        base_reply, base_source = self._get_institutional_base_answer(message, language=language)
        if base_reply:
            db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
            db_service.save_chat_message(session_id, role="assistant", content=base_reply, student_language=language)
            return {
                "reply": base_reply,
                "answer": base_reply,
                "source_url": base_source,
                "sources": [{"title": "بوابة الجامعة الأردنية فرع العقبة", "url": base_source}] if base_source else [],
                "session_id": session_id
            }

        # Intent 5: Actual University Inquiries - Run ChromaDB Vector Search + Gemini
        session_record = db_service.get_chat_history(session_id)
        history = session_record.get("messages", []) if session_record else []

        vector_results = vector_service.similarity_search(message, top_k=5)
        retrieved_texts = []
        sources = []
        seen_urls = set()
        primary_source_url = None

        for match in vector_results:
            retrieved_texts.append(match["text"])
            meta = match.get("metadata", {})
            url = meta.get("url") or meta.get("source_url")
            title = meta.get("title") or "موقع الجامعة الأردنية فرع العقبة"
            if url and url not in seen_urls:
                if not primary_source_url:
                    primary_source_url = url
                seen_urls.add(url)
                sources.append({"title": title, "url": url})

        context_str = "\n---\n".join(retrieved_texts)

        reply_text = self.generate_gemini_answer(
            query=message,
            retrieved_context=context_str,
            citations=sources,
            history=history,
            language=language
        )

        final_source_url = None

        if reply_text:
            # Check if Gemini produced an out-of-scope redirection or refusal
            is_refusal = any(p in reply_text for p in ["عذراً منك، أنا مساعدك الأكاديمي", "I apologize, but I am 'Rafeeq'"])
            if not is_refusal:
                final_source_url = primary_source_url or "https://aqaba.ju.edu.jo"
        else:
            # Fallback ONLY for actual factual university questions
            is_factual_uni_q = any(k in q_norm for k in ["متى", "اين", "وين", "كم", "شروط", "عميد", "امتحان", "سحب", "اضاف", "تسجيل", "كلية", "دوام", "رسوم", "موعد", "معدل", "تخصص", "when", "where", "how", "requirements", "dean", "exam", "dates"])
            if is_factual_uni_q:
                if language == "ar":
                    reply_text = "بحثت في السجلات الحالية لفرع العقبة ولم أجد تاريخاً/اسماً معلناً لهذه النقطة تحديداً حتى اللحظة، لكن يمكنك متابعة الإعلانات عبر الرابط التالي: https://aqaba.ju.edu.jo"
                else:
                    reply_text = "I checked the current records for the Aqaba branch and found no declared date/name for this specific query at this time. You can follow announcements via: https://aqaba.ju.edu.jo"
                final_source_url = "https://aqaba.ju.edu.jo"
            else:
                if language == "ar":
                    reply_text = "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!"
                else:
                    reply_text = "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch). I would be more than happy to help you with any questions related to university majors, facilities, or student services!"
                final_source_url = None

        db_service.save_chat_message(session_id, role="user", content=message, student_language=language)
        db_service.save_chat_message(session_id, role="assistant", content=reply_text, student_language=language)

        return {
            "reply": reply_text,
            "answer": reply_text,
            "source_url": final_source_url,
            "sources": sources if final_source_url else [],
            "session_id": session_id
        }

rag_service = RAGService()
