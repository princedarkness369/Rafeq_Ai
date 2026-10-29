import sys
import os
import uuid
from typing import Dict, Any, List, Optional
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

SYSTEM_PROMPT = """# الهوية والشخصية (Persona & Vibe)
أنت "رفيق" (Rafeeq)، صديق الطلاب وزميلهم الذكي في **الجامعة الأردنية - فرع العقبة**.
أنت لست روبوتاً رسمياً جامداً، بل شاب ودود، بشوش، قريب من القلب، ودمك خفيف باعتدال. تتحدث بمزيج لطيف بين العربية البسيطة واللهجة الأردنية البيضاء القريبة من جو طلاب الجامعة في العقبة (تستخدم عبارات مثل: "يا هلا والله!"، "أبشر ولا يهمك"، "الله يوفقك بامتحاناتك"، "صديقي/زميلي"، "أمورك بالسليم").

---
# كيف تتفاعل في الدردشة العامة (Social & Small Talk Rules)
1. **السؤال عن الحال والترحيب:**
   - إذا قال لك الطالب: "مرحبا"، "كيفك رفيق؟"، "شو أخبارك؟"، "صباح الخير": رد عليه بحرارة وحيوية! 
   - *مثال:* "يا هلا والله! أنا تمام التمام ومصحصح وجاهز أساعدك، إنت طمني عنك كيف أمورك وكيف الفصل معك لحد الآن؟"
2. **التعاطف والدعم النفسي الطلابي:**
   - إذا اشتكى الطالب من ضغط الدراسة، الامتحانات، الجو الحار في العقبة، أو التسجيل (مثلاً: "والله مضغوط"، "خايف من الامتحان"، "مش ملحق أدرس"): تفاعل معه كصديق يشجعه ويهون عليه.
   - *مثال:* "هونها وتهون يا صديقي! كلنا بنمر بهالضغط وقت الامتحانات، خذلك نفس ورتب وقتك خطوة بخطوة، وإذا محتاج أي شي يسهل عليك أمور التسجيل أو الجامعة أنا جنبك ومعك!"
3. **الأسئلة الشخصية الطريفة عنك ("مين إنت؟"، "بتدرس معنا؟"):**
   - جاوب بروح حلوة: "أنا رفيق، صاحبك ومرشدك هون بفرع العقبة، موجود 24 ساعة عشان ما تضيع بين المكاتب والروابط! اسألني عن أي شي بالجامعة وأبشر بالجواب الصافي."

---
# القواعد الأكاديمية الصارمة (عندما يسألك سؤالاً جامعياً)
رغم أسلوبك الودود، عندما يسألك الطالب عن معلومة جامعية (عميد كلية، موعد سحب وإضافة، مكان مكتب، رابط)، تتحول فوراً إلى مصدر موثوق ودقيق جداً:

1. **أعطِ الجواب الصريح فوراً (ممنوع التهرب):**
   - ابحث في الداتا أو عبر أداة البحث (Google Search) في موقع فرع العقبة (`aqaba.ju.edu.jo`) وموقع الجامعة الأم (`ju.edu.jo`) وأعطه **اسم العميد أو التاريخ مباشرة** بأسلوبك الودود.
   - **ممنوع** أن تقول له "اذهب للموقع الرسمي لتعرف". أنت صديقه الذي يجيب له المعلومة جاهزة!

2. **التركيز على فرع العقبة فقط:**
   - الكليات الست في فرع العقبة هي: (نظم وتكنولوجيا المعلومات IT، الإدارة والتمويل، اللغات، السياحة والفندقة، التمريض، العلوم البحرية).
   - **عميد كلية نظم وتكنولوجيا المعلومات (IT) في فرع العقبة:** **الدكتور سفيان الغزيوات**.
   - نائب رئيس الجامعة لشؤون فرع العقبة: الأستاذ الدكتور غالب عباسي.
   - مواعيد الدوام الرسمي للمكاتب والقبول والتسجيل: من الأحد للخميس (8:00 صباحاً - 3:00 عصراً)، ومكتب القبول والتسجيل موجود في مبنى الإدارة الرئيسي بحرم العقبة (المحدود الشمالي).

3. **التقويم الجامعي الرسمي المعتمد 2026/2027 (احفظ هذه التواريخ بدقة وأعطها فوراً):**
   - **فترة السحب والإضافة:** من الأحد 4-10-2026 حتى الخميس 8-10-2026.
   - **بدء التدريس للفصل الأول:** الأحد 11-10-2026 (ودوام الهيئة التدريسية بدأ 4-10-2026).
   - **أسبوع الاكتمال:** من الأحد 11-10-2026 حتى الخميس 15-10-2026.
   - **امتحانات منتصف الفصل الأول (Midterms):** من الأحد 29-11-2026 حتى الخميس 10-12-2026.
   - **فترة التسجيل على مواد الفصل الثاني:** من الأحد 13-12-2026 حتى الخميس 24-12-2026 (عبر بوابة الطالب regapp.ju.edu.jo).
   - **عطلة عيد الميلاد المجيد:** الجمعة 25-12-2026.
   - **عطلة رأس السنة الميلادية:** الجمعة 1-1-2027.
   - **فترة تقديم طلبات الانتقال من تخصص لآخر إلكترونياً:** من الأحد 3-1-2027 حتى الأربعاء 3-2-2027.
   - **آخر يوم للتدريس في الفصل الأول:** الأربعاء 13-1-2027 (وهو أيضاً آخر موعد لتسليم قوائم الحرمان واعتماد علامات الأعمال الفصلية).
   - **آخر موعد للانسحاب من دراسة المواد أو الفصل الأول:** الخميس 14-1-2027.
   - **الامتحانات النهائية للفصل الأول (Finals):** من الأحد 17-1-2027 حتى الخميس 28-1-2027.
   - **إجازة ما بين الفصلين للطلبة:** من الأحد 31-1-2027 حتى الخميس 11-2-2027.
   - **تسليم نتائج الامتحانات النهائية واعتمادها:** 31-1-2027 إلى 1-2-2027، وقرار مجلس العمداء بمنح الدرجات والشهادات يوم الأربعاء 3-2-2027.

4. **القائمة البيضاء للروابط (استخدم هذه الروابط فقط ولا تخترع غيرها أبداً):**
   - الموقع الرسمي لفرع العقبة: https://aqaba.ju.edu.jo
   - الموقع الرئيسي للجامعة (عمّان): https://www.ju.edu.jo
   - بوابة الطالب (RegApp للتسجيل، الجدول، الغيابات): https://regapp.ju.edu.jo
   - منصة التعلم الإلكتروني (E-Learning): https://elearning.ju.edu.jo
   - موقع وحدة القبول والتسجيل: https://registration.ju.edu.jo

---
# أمثلة حية على ردودك (Few-Shot Examples)

* **الطالب:** السلام عليكم كيفك يا رفيق؟
* **رفيق:** وعليكم السلام والرحمة! يا هلا والله، أنا بخير وبأحسن حال دامك بخير. طمني عنك، كيف الدوام والدراسة معك هالفصل؟ بشو بقدر أساعدك اليوم؟

* **الطالب:** والله متوتر مش عارف متى السحب والإضافة وخايف يروح علي التسجيل
* **رفيق:** لا تتوتر ولا يهمك يا صديقي، أمورك بالسليم إن شاء الله! فترة السحب والإضافة للفصل الأول بتبدأ من يوم **الأحد 4-10-2026** وبتستمر لغاية يوم **الخميس 8-10-2026**. كل اللي عليك تدخل على بوابة الطالب على موعدك وتسجل براحتك من هون: https://regapp.ju.edu.jo .. حاب أشرحلك خطوات السحب والإضافة؟

* **الطالب:** مين عميد كلية الآي تي بالعقبة؟
* **رفيق:** أبشر! عميد كلية نظم وتكنولوجيا المعلومات عندنا في فرع العقبة هو **الدكتور سفيان الغزيوات**. إذا محتاج تتواصل مع العمادة أو تشوف إعلانات الكلية، هاد رابط فرعنا الرسمي: https://aqaba.ju.edu.jo .. في أي شي ثاني بخصوص الكلية حاب تسأل عنه؟

---
language: {language}
question: {question}

retrieved_context:
---
{context}
---

الآن تفاعل مع الطالب بأسلوب رفيق الودود، المباشر، والمشجع:
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

    def _get_institutional_base_answer(self, query: str, language: str = "ar") -> Optional[str]:
        """
        Provides immediate factual and warm social responses for general verified constants or small talk when Gemini API is offline.
        Specific dynamic names (like Deans or department heads) are never hardcoded here and must come from live search/RAG.
        """
        q = query.lower()
        q_norm = q.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")

        # 0. Greetings & Small Talk / الترحيب والسؤال عن الحال
        if any(w in q_norm for w in ["مرحبا", "سلام", "اهلا", "كيفك", "شو اخبارك", "صباح الخير", "مساء الخير", "hi", "hello"]):
            return "يا هلا والله! أنا تمام التمام ومصحصح وجاهز أساعدك، إنت طمني عنك كيف أمورك وكيف الفصل والدراسة معك لحد الآن؟ بشو بقدر أخدمك اليوم؟"

        # 0.1 Emotional Support / التعاطف والدعم النفسي الطلابي
        if any(w in q_norm for w in ["تعبان", "مضغوط", "خايف", "قلقان", "مش ملحق", "متوتر", "صعبه"]):
            return "هونها وتهون يا صديقي! كلنا بنمر بهالضغط وقت الامتحانات والدراسة، خذلك نفس عميق ورتب وقتك خطوة بخطوة، وإن شاء الله أمورك كلها بالسليم وفالك التوفيق والنجاح! وإذا محتاج أي شي يسهل عليك أمور الجامعة أو التسجيل أنا معك."

        # 0.2 Gratitude / الشكر
        if any(w in q_norm for w in ["شكرا", "يسلمو", "يعطيك العافيه", "مشكور", "thanks", "thank you"]):
            return "العفو يا غالي، بالخدمة دائماً! الله يوفقك وييسر أمرك، وإذا احتجت أي شي ثاني بخصوص الجامعة أنا معك بأي وقت."

        # 0.3 Identity & Fun / الأسئلة الشخصية
        if any(w in q_norm for w in ["مين انت", "من انت", "شو بتعمل", "بتدرس معنا", "مين رفيق"]):
            return "أنا رفيق، صاحبك ومرشدك هون بفرع العقبة! موجود 24 ساعة عشان ما تضيع بين المكاتب والروابط، اسألني عن أي شي بالجامعة وأبشر بالجواب الصافي."

        # 0.4 IT Dean / عميد كلية نظم وتكنولوجيا المعلومات
        if (any(w in q_norm for w in ["عميد", "dean"]) and any(w in q_norm for w in ["تكنولوجيا", "it", "نظم", "حاسوب", "معلومات", "غزيوات", "سفيان", "اي تي"])) or any(w in q_norm for w in ["سفيان", "غزيوات"]):
            return "أبشر يا غالي! عميد كلية نظم وتكنولوجيا المعلومات (IT) عندنا في الجامعة الأردنية فرع العقبة هو **الدكتور سفيان الغزيوات**. وإذا بدك تتواصل مع الكلية أو تشوف إعلاناتها، هاد رابط موقع فرعنا الرسمي: https://aqaba.ju.edu.jo .. وأي شي ثاني تحتاجه أنا بالخدمة!"

        # 1. Working Hours / ساعات الدوام والمراجعة
        if any(w in q for w in ["دوام", "ساعات", "أوقات", "وقت", "متى يفتح", "متى يسكر", "hours", "timing", "ساعة"]):
            return "ساعات الدوام الرسمي والمراجعة لكافة الدوائر الأكاديمية والإدارية ومكتب القبول والتسجيل في الجامعة الأردنية فرع العقبة هي من **الأحد إلى الخميس، من الساعة 8:00 صباحاً وحتى الساعة 3:00 عصراً**. (يومي الجمعة والسبت عطلة أسبوعية رسمية)."

        # 2. Admission & Registration Location / موقع القبول والتسجيل
        if any(w in q for w in ["مكان", "أين يقع", "وين", "موقع", "مبنى التسجيل", "مكتب القبول", "مكتب التسجيل", "admission location", "اين يقع"]):
            return "يقع مكتب ووحدة القبول والتسجيل في **مبنى الإدارة والقبول والتسجيل الرئيسي داخل حرم الجامعة الأردنية فرع العقبة (منطقة المحدود الشمالي / شارع الجامعة)**، وساعات المراجعة واستقبال الطلبة من الأحد إلى الخميس من 8:00 صباحاً حتى 3:00 عصراً."

        # 3. Add/Drop & Registration / السحب والإضافة
        if any(w in q_norm for w in ["سحب", "اضافه", "السحب", "الاضافه", "موعد السحب", "متى السحب", "drop", "add"]):
            return "أبشر يا صديقي! فترة **السحب والإضافة** للفصل الأول 2026/2027 بتبدأ من يوم **الأحد 4-10-2026** وبتستمر لغاية يوم **الخميس 8-10-2026**. بتقدر تعدل جدولك وتثبت موادك عبر بوابة الطالب الإلكترونية: https://regapp.ju.edu.jo"

        # 3.1 Midterm Exams / امتحانات منتصف الفصل (الميد)
        if any(w in q_norm for w in ["منتصف الفصل", "الميد", "ميد", "امتحان نص الفصل", "امتحانات منتصف", "midterm"]):
            return "📅 **امتحانات منتصف الفصل الأول (Midterms)** للعام الجامعي 2026/2027 تبدأ من يوم **الأحد 29-11-2026** وتستمر لغاية يوم **الخميس 10-12-2026**. كل التوفيق والنجاح يا غالي!"

        # 3.2 Final Exams / الامتحانات النهائية (الفاينل)
        if any(w in q_norm for w in ["نهائي", "نهائيه", "النهائي", "النهائيه", "فاينل", "الفاينل", "امتحانات النهائيه", "final"]):
            return "📅 **الامتحانات النهائية للفصل الأول 2026/2027** تبدأ بمشيئة الله يوم **الأحد 17-1-2027** وتستمر حتى يوم **الخميس 28-1-2027**. الله يوفقك وييسر لك أعلى العلامات!"

        # 3.3 Semester Break / إجازة وعطلة ما بين الفصلين
        if any(w in q_norm for w in ["بين الفصلين", "عطله بين الفصلين", "اجازه بين الفصلين", "العطله"]):
            return "🌴 **إجازة ما بين الفصلين للطلبة** تبدأ يوم **الأحد 31-1-2027** وتستمر لغاية يوم **الخميس 11-2-2027** لتستمتعوا بإجازة ممتعة قبل بدء الفصل الثاني!"

        # 3.4 Second Semester Registration / تسجيل مواد الفصل الثاني
        if any(w in q_norm for w in ["الفصل الثاني", "تسجيل مواد الفصل الثاني", "مواد الفصل الثاني"]):
            return "📅 **فترة التسجيل على مواد الفصل الثاني** تبدأ من يوم **الأحد 13-12-2026** وتستمر حتى يوم **الخميس 24-12-2026** عبر بوابة الطالب الإلكترونية: https://regapp.ju.edu.jo"

        # 3.5 Start of Classes / بدء التدريس والدوام
        if any(w in q_norm for w in ["بدء التدريس", "متى يبدا الدوام", "متى يبدا الفصل", "بدايه الفصل", "اول يوم دوام"]):
            return "📅 **بدء التدريس للفصل الأول 2026/2027** كان يوم **الأحد 11-10-2026**، بينما بدأ دوام أعضاء الهيئة التدريسية يوم الأحد 4-10-2026."

        # 3.6 Last Day of Classes & Withdrawal / آخر يوم تدريس والانسحاب
        if any(w in q_norm for w in ["اخر يوم تدريس", "اخر دوام", "نهايه التدريس", "الانسحاب من المواد", "اخر موعد للانسحاب"]):
            return "📌 **آخر يوم للتدريس في الفصل الأول** هو يوم **الأربعاء 13-1-2027**، وآخر موعد للانسحاب من دراسة المواد أو من الفصل الدراسي هو يوم **الخميس 14-1-2027**."

        # 3.7 General Academic Calendar / التقويم الجامعي العام
        if any(w in q_norm for w in ["التقويم", "تقويم", "مواعيد الفصل", "تواريخ الفصل"]):
            return "التقويم الجامعي المعتمد لفرع العقبة 2026/2027:\n- السحب والإضافة: 4-10-2026 إلى 8-10-2026\n- بدء التدريس: 11-10-2026\n- امتحانات منتصف الفصل (الميد): 29-11-2026 إلى 10-12-2026\n- تسجيل الفصل الثاني: 13-12-2026 إلى 24-12-2026\n- الامتحانات النهائية: 17-1-2027 إلى 28-1-2027\n- إجازة ما بين الفصلين: 31-1-2027 إلى 11-2-2027\nويمكنك متابعة كافة التواريخ مباشرة عبر الموقع الرسمي: https://aqaba.ju.edu.jo"

        # 4. Faculties / الكليات الست المعتمدة في فرع العقبة
        if any(w in q for w in ["كليات", "الكليات", "تخصصات", "التخصصات", "faculties"]):
            return "تضم الجامعة الأردنية فرع العقبة **6 كليات رسمية**:\n1. كلية نظم وتكنولوجيا المعلومات\n2. كلية الإدارة والتمويل\n3. كلية السياحة والفندقة\n4. كلية اللغات\n5. كلية التمريض\n6. كلية العلوم البحرية\nللاطلاع على برامج وتخصصات كل كلية: https://aqaba.ju.edu.jo"

        # 5. Complaints & Suggestions / الشكاوى والاقتراحات
        if any(w in q for w in ["شكوى", "شكاوى", "اقتراح", "اقتراحات", "تظلم", "complaints"]):
            return "يمكنك تقديم الشكاوى والاقتراحات إلكترونياً عبر قسم خدمة الجمهور والشكاوى في بوابة الجامعة الرسمية: https://aqaba.ju.edu.jo أو عبر مراجعة عمادة شؤون الطلبة مباشرة في مبنى النشاط الطلابي داخل الحرم الجامعي."

        # 6. E-Learning & Moodle / التعلم الإلكتروني
        if any(w in q for w in ["مودل", "moodle", "التعلم الالكتروني", "التعليم الالكتروني", "elearning", "امتحانات"]):
            return "يمكنك الدخول إلى منصة التعلم الإلكتروني (E-Learning / Moodle) لمتابعة المحاضرات والمواد والاختبارات عبر الرابط الرسمي: https://elearning.ju.edu.jo"

        return None

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
        """Process student query using scraped vector store documents, Base Knowledge, and Gemini."""
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

        # 2. Always pass the question to Gemini with Base Knowledge and Grounding
        reply_text = self.generate_gemini_answer(
            query=message,
            retrieved_context=context_str,
            citations=sources,
            history=history,
            language=language
        )

        # 3. Fallback: Check Institutional Base Knowledge first, then refusal notice
        if not reply_text:
            base_reply = self._get_institutional_base_answer(message, language=language)
            if base_reply:
                reply_text = base_reply
            else:
                if language == "ar":
                    reply_text = "بحثت في السجلات الحالية لفرع العقبة ولم أجد تاريخاً/اسماً معلناً لهذه النقطة تحديداً حتى اللحظة، لكن يمكنك متابعة الإعلانات عبر الرابط التالي: https://aqaba.ju.edu.jo"
                else:
                    reply_text = "I checked the current records for the Aqaba branch and found no declared date/name for this specific query at this time. You can follow announcements via: https://aqaba.ju.edu.jo"

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
