import os
import sys
import uuid
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

# Ensure UTF-8 output encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Google Gemini GenAI Client Initialization
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    types = None

api_key = os.getenv("GEMINI_API_KEY", "")
gemini_client = None

if api_key and GENAI_AVAILABLE:
    try:
        if api_key.startswith("AQ."):
            gemini_client = genai.Client(vertexai=True, api_key=api_key)
        else:
            gemini_client = genai.Client(api_key=api_key)
        print("[HuggingFace Space] Gemini client successfully initialized.")
    except Exception as e:
        print(f"[HuggingFace Space Error] Gemini init error: {e}")

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

5. **Pure Language Output:**
   - In Arabic, use pure Arabic titles without parentheses containing English acronyms (e.g., use "بوابة التسجيل الذاتي للطلبة", "منصة التعلم الإلكتروني", "كلية تكنولوجيا المعلومات").
   - In English, provide complete, fluent English.

---
# Institutional Knowledge & Verified Data (University of Jordan - Aqaba Branch)

1. **Colleges & Deans Directory:**
   - **كلية تكنولوجيا المعلومات:** العميد **الدكتور سفيان الغزيوات**
   - **كلية إدارة الأعمال:** العميد **الدكتور عمر سنجلاوي**
   - **كلية السياحة والفندقة:** العميد **الدكتور عمر جوابرة**
   - **كلية التمريض:** العميد **الدكتور محمود الكلالدة**
   - **كلية الأحياء:** العميد **الدكتور محمود الكلالدة**
   - **كلية الرياضيات:** العميد **الدكتور محمود الكلالدة**
   - **كلية اللغات:** عمادة كلية اللغات
   - دليل الهيئة التدريسية: https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx
   - نائب رئيس الجامعة لشؤون فرع العقبة: الأستاذ الدكتور غالب عباسي.
   - ساعات الدوام الرسمي: الأحد إلى الخميس، من 8:00 صباحاً وحتى 3:00 عصراً (مبنى الإدارة والقبول والتسجيل الرئيسي، المحدود الشمالي).

2. **Academic Calendar 2026/2027:**
   - **فترة السحب والإضافة:** الأحد 4-10-2026 حتى الخميس 8-10-2026
   - **بدء التدريس للفصل الأول:** الأحد 11-10-2026
   - **امتحانات منتصف الفصل الدراسي:** الأحد 29-11-2026 حتى الخميس 10-12-2026
   - **فترة التسجيل على مواد الفصل الثاني:** الأحد 13-12-2026 حتى الخميس 24-12-2026
   - **عطلة عيد الميلاد المجيد:** الجمعة 25-12-2026
   - **عطلة رأس السنة الميلادية:** الجمعة 1-1-2027
   - **فترة تقديم طلبات الانتقال من تخصص لآخر:** الأحد 3-1-2027 حتى الأربعاء 3-2-2027
   - **آخر يوم للتدريس في الفصل الأول:** الأربعاء 13-1-2027
   - **آخر موعد للانسحاب من دراسة المواد:** الخميس 14-1-2027
   - **الامتحانات النهائية للفصل الأول:** الأحد 17-1-2027 حتى الخميس 28-1-2027
   - **إجازة ما بين الفصلين للطلبة:** الأحد 31-1-2027 حتى الخميس 11-2-2027

3. **Whitelisted Official Portals:**
   - موقع فرع العقبة الرسمي: https://aqaba.ju.edu.jo
   - بوابة التسجيل الذاتي للطلبة: https://ujapps.ju.edu.jo/selfregappaq/
   - منصة التعلم الإلكتروني المعتمدة: https://elearning.ju.edu.jo
   - نظام تقديم الشكاوى والاقتراحات: https://eservices.ju.edu.jo/complaintsys/login.aspx
   - وحدة القبول والتسجيل: https://registration.ju.edu.jo
   - دليل الكليات وأعضاء الهيئة التدريسية: https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx

---
language: {language}
question: {question}

الآن حلل السؤال وقدم إجابتك الاحترافية الموثقة:
"""

def get_base_institutional_answer(query: str, language: str = "ar") -> Tuple[Optional[str], Optional[str]]:
    q = query.lower()
    q_norm = q.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

    # IT Dean
    if any(w in q_norm for w in ["سفيان", "غزيوات"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["تكنولوجيا", "it", "نظم", "حاسوب", "معلومات", "اي تي"])):
        ans = "Dean of Faculty of IT is Dr. Sufyan Al-Ghazaiwat." if language == "en" else "أهلاً بك! عميد كلية تكنولوجيا المعلومات في الجامعة الأردنية فرع العقبة هو **الدكتور سفيان الغزيوات**."
        return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

    # Business Dean
    if any(w in q_norm for w in ["سنجلاوي", "عمر سنجلاوي"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["اداره", "اعمال", "الاعمال", "تمويل", "بزنس", "business"])):
        ans = "Dean of Faculty of Business is Dr. Omar Sinjilawi." if language == "en" else "أهلاً بك! عميد كلية إدارة الأعمال في الجامعة الأردنية فرع العقبة هو **الدكتور عمر سنجلاوي**."
        return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

    # Tourism Dean
    if any(w in q_norm for w in ["جوابره", "عمر جوابره"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["سياحه", "فندقه", "سياحة", "tourism"])):
        ans = "Dean of Faculty of Tourism & Hospitality is Dr. Omar Jawbrah." if language == "en" else "أهلاً بك! عميد كلية السياحة والفندقة في الجامعة الأردنية فرع العقبة هو **الدكتور عمر جوابرة**."
        return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

    # Nursing, Biology, Math
    if any(w in q_norm for w in ["كلالده", "محمود الكلالده"]) or ((any(w in q_norm for w in ["عميد", "dean"])) and any(w in q_norm for w in ["تمريض", "التمريض", "احياء", "الاحياء", "رياضيات", "الرياضيات", "علوم بحريه", "علوم اساسيه"])):
        ans = "Dean of Faculty of Nursing, Biology, and Mathematics is Dr. Mahmoud Al-Kalaldah." if language == "en" else "أهلاً بك! عميد كلية التمريض، وكلية الأحياء، وكلية الرياضيات في فرع العقبة هو **الدكتور محمود الكلالدة**."
        return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

    # General Deans Question
    if any(w in q_norm for w in ["عمداء الكليات", "مين هم العمداء", "اسماء العمداء", "من هم العمداء", "who are the deans"]):
        ans = (
            "Faculty Deans at UJ Aqaba:\n• IT: Dr. Sufyan Al-Ghazaiwat\n• Business: Dr. Omar Sinjilawi\n• Tourism: Dr. Omar Jawbrah\n• Nursing, Biology & Math: Dr. Mahmoud Al-Kalaldah"
            if language == "en" else
            "عمداء كليات الجامعة الأردنية فرع العقبة المعتمدين:\n• **كلية تكنولوجيا المعلومات:** د. سفيان الغزيوات\n• **كلية إدارة الأعمال:** د. عمر سنجلاوي\n• **كلية السياحة والفندقة:** د. عمر جوابرة\n• **كلية التمريض:** د. محمود الكلالدة\n• **كلية الأحياء:** د. محمود الكلالدة\n• **كلية الرياضيات:** د. محمود الكلالدة"
        )
        return ans, "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"

    # Self-Registration Portal
    if any(w in q_norm for w in ["بوابه التسجيل", "تسجيل ذاتي", "التسجيل الذاتي", "سيلف ريج", "selfreg"]):
        ans = "The official student self-registration portal for UJ Aqaba is: https://ujapps.ju.edu.jo/selfregappaq/" if language == "en" else "رابط بوابة التسجيل الذاتي للطلبة في الجامعة الأردنية فرع العقبة هو: https://ujapps.ju.edu.jo/selfregappaq/"
        return ans, "https://ujapps.ju.edu.jo/selfregappaq/"

    # Complaints & Suggestions
    if any(w in q_norm for w in ["شكوى", "شكاوى", "اقتراح", "اقتراحات", "complaints"]):
        ans = "You can submit electronic complaints and suggestions via: https://eservices.ju.edu.jo/complaintsys/login.aspx" if language == "en" else "يمكنك تقديم الشكاوى والاقتراحات إلكترونياً عبر قسم خدمة الجمهور والشكاوى في بوابة الجامعة الرسمية: https://eservices.ju.edu.jo/complaintsys/login.aspx"
        return ans, "https://eservices.ju.edu.jo/complaintsys/login.aspx"

    # Working Hours
    if any(w in q for w in ["دوام", "ساعات", "أوقات", "وقت", "متى يفتح", "متى يسكر", "hours", "timing"]):
        ans = "Official working hours at UJ Aqaba are Sunday to Thursday, 8:00 AM – 3:00 PM." if language == "en" else "ساعات الدوام الرسمي لكافة دوائر ومكاتب الجامعة الأردنية فرع العقبة هي من **الأحد إلى الخميس، من 8:00 صباحاً وحتى 3:00 عصراً**."
        return ans, "https://registration.ju.edu.jo"

    # Add/Drop
    if any(w in q_norm for w in ["سحب", "اضافه", "السحب", "الاضافه", "drop", "add"]):
        ans = "Add/Drop period for First Semester 2026/2027 runs from October 4, 2026 to October 8, 2026." if language == "en" else "فترة **السحب والإضافة** للفصل الأول 2026/2027 تبدأ من **الأحد 4-10-2026** وتستمر حتى **الخميس 8-10-2026** عبر بوابة التسجيل الذاتي للطلبة."
        return ans, "https://ujapps.ju.edu.jo/selfregappaq/"

    # Midterms
    if any(w in q_norm for w in ["منتصف الفصل", "الميد", "ميد", "midterm"]):
        ans = "Midterm exams run from November 29, 2026 to December 10, 2026." if language == "en" else "📅 **امتحانات منتصف الفصل الدراسي الأول** تبدأ من يوم **الأحد 29-11-2026** وتستمر لغاية يوم **الخميس 10-12-2026**."
        return ans, "https://aqaba.ju.edu.jo"

    # Finals
    if any(w in q_norm for w in ["نهائي", "نهائيه", "النهائي", "فاينل", "final"]):
        ans = "Final exams run from January 17, 2027 to January 28, 2027." if language == "en" else "📅 **الامتحانات النهائية للفصل الأول 2026/2027** تبدأ يوم **الأحد 17-1-2027** وتستمر حتى يوم **الخميس 28-1-2027**."
        return ans, "https://aqaba.ju.edu.jo"

    # E-Learning
    if any(w in q_norm for w in ["مودل", "moodle", "التعلم الالكتروني", "elearning"]):
        ans = "Official E-Learning platform link: https://elearning.ju.edu.jo" if language == "en" else "يمكنك الدخول إلى منصة التعلم الإلكتروني المعتمدة عبر الرابط: https://elearning.ju.edu.jo"
        return ans, "https://elearning.ju.edu.jo"

    return None, None

def answer_student_query(message: str, language: str = "ar") -> Dict[str, Any]:
    q = message.strip()
    q_norm = q.lower().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

    # Intent 1: Greetings (No conversational baiting, NO source link)
    greeting_words = ["مرحبا", "سلام", "اهلا", "كيفك", "شو اخبارك", "صباح الخير", "مساء الخير", "hello", "hi", "hey"]
    if any(w in q_norm for w in greeting_words) and len(q_norm.split()) <= 4 and not any(k in q_norm for k in ["جامع", "كلي", "تسجيل", "عميد", "سحب", "امتحان", "دوام"]):
        reply = "Hello! I am Rafeeq, your official academic assistant for the University of Jordan (Aqaba Branch). How can I assist you with your university inquiries today?" if language == "en" else "أهلاً بك! أنا رفيق، مرشدك الأكاديمي في الجامعة الأردنية فرع العقبة. كيف يمكنني مساعدتك في استفساراتك الأكاديمية والجامعية اليوم؟"
        return {"reply": reply, "source_url": None, "sources": []}

    # Intent 2: Personal statements & exam stress (NO database search, NO record fallback, NO source link)
    personal_phrases = ["علي امتحان", "عندي امتحان", "امتحان بكره", "درست كثير", "تعبان", "حاس بضغط", "مضغوط", "مش ملحق", "نعسان", "خايف", "i have an exam", "feeling tired", "stressed"]
    if any(p in q_norm for p in personal_phrases) and not any(k in q_norm for k in ["متى", "اين", "وين", "كم", "شروط", "عميد", "موعد الامتحان", "when", "where"]):
        reply = "I wish you all the best and great success! My role is strictly dedicated to answering official inquiries regarding the University of Jordan (Aqaba Branch). Do you have a specific university inquiry I can assist you with?" if language == "en" else "أتمنى لك كل التوفيق والنجاح! يقتصر دوري كمساعد أكاديمي رسمي على الإجابة عن استفسارات الجامعة الأردنية فرع العقبة الرسمية والأنظمة ومواعيد التسجيل ومرافق الكليات. هل لديك استفسار محدد بخصوص المواد أو الجداول لمساعدتك به؟"
        return {"reply": reply, "source_url": None, "sources": []}

    # Intent 3: Out-of-Scope (No source link)
    out_of_scope = ["هل انت من الاردن", "انت من الاردن", "are you from jordan", "عاصمه الاردن", "capital of jordan", "احكيلي نكته", "tell me a joke"]
    if any(p in q_norm for p in out_of_scope) and not any(k in q_norm for k in ["جامع", "كلي", "تسجيل", "عميد"]):
        reply = "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch). I would be more than happy to help you with any questions related to university majors, facilities, or student services!" if language == "en" else "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!"
        return {"reply": reply, "source_url": None, "sources": []}

    # Intent 4: Base Knowledge
    base_ans, base_source = get_base_institutional_answer(message, language=language)
    if base_ans:
        return {"reply": base_ans, "source_url": base_source, "sources": [{"title": "بوابة الجامعة الرسمية", "url": base_source}] if base_source else []}

    # Intent 5: Gemini AI Generation
    if gemini_client:
        try:
            full_prompt = SYSTEM_PROMPT.format(language="ar" if language == "ar" else "en", question=message)
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            if response and response.text:
                rep = response.text.strip()
                is_refusal = any(p in rep for p in ["عذراً منك، أنا مساعدك الأكاديمي", "I apologize, but I am 'Rafeeq'"])
                source_url = None if is_refusal else "https://aqaba.ju.edu.jo"
                return {"reply": rep, "source_url": source_url, "sources": [{"title": "بوابة الجامعة الأردنية فرع العقبة", "url": source_url}] if source_url else []}
        except Exception as e:
            print(f"[Gemini Exception] {e}")

    # Fallback ONLY for actual factual university queries
    is_factual_uni = any(k in q_norm for k in ["متى", "اين", "وين", "كم", "شروط", "عميد", "امتحان", "سحب", "اضاف", "تسجيل", "كلية", "دوام"])
    if is_factual_uni:
        reply = "بحثت في السجلات الحالية لفرع العقبة ولم أجد تاريخاً/اسماً معلناً لهذه النقطة تحديداً حتى اللحظة، لكن يمكنك متابعة الإعلانات عبر الرابط التالي: https://aqaba.ju.edu.jo" if language == "ar" else "I checked current records for the Aqaba branch and found no declared date/name for this specific query at this time. You can follow announcements via: https://aqaba.ju.edu.jo"
        return {"reply": reply, "source_url": "https://aqaba.ju.edu.jo", "sources": [{"title": "بوابة الجامعة الأردنية فرع العقبة", "url": "https://aqaba.ju.edu.jo"}]}

    reply = "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!" if language == "ar" else "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch)."
    return {"reply": reply, "source_url": None, "sources": []}

# 2. Gradio Interface (Native Hugging Face Runner)
def gradio_chat(user_message, history):
    res = answer_student_query(user_message, language="ar")
    bot_reply = res["reply"]
    if res["source_url"]:
        bot_reply += f"\n\n🔗 **المصدر الرسمي:** {res['source_url']}"
    return bot_reply

with gr.Blocks(title="Rafeeq - UJ Aqaba Academic Assistant") as demo:
    gr.Markdown("""
    # 🟢 Rafeeq Backend API is Online (`my_rafeeq`)
    ### المرشد الأكاديمي الذكي — الجامعة الأردنية فرع العقبة
    خادم الـ API يعمل بنجاح وجاهز لاستقبال طلبات الواجهة الأمامية عبر:
    `POST /api/chat`
    """)
    chatbot = gr.Chatbot(label="محادثة رفيق الأكاديمي", height=420)
    msg = gr.Textbox(label="اكتب استفسارك الأكاديمي هنا:", placeholder="اسأل عن الكليات، العمداء، التقويم الجامعي، بوابة التسجيل الذاتي...")
    with gr.Row():
        send_btn = gr.Button("إرسال", variant="primary")
        clear_btn = gr.Button("مسح")

    def user_fn(user_message, history):
        if not user_message or not user_message.strip():
            return "", history or []
        history = history or []
        history.append((user_message, None))
        return "", history

    def bot_fn(history):
        if not history:
            return history
        user_message = history[-1][0]
        bot_reply = gradio_chat(user_message, history)
        history[-1] = (user_message, bot_reply)
        return history

    msg.submit(user_fn, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_fn, chatbot, chatbot
    )
    send_btn.click(user_fn, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_fn, chatbot, chatbot
    )
    clear_btn.click(lambda: None, None, chatbot, queue=False)

# 3. Register Custom FastAPI Endpoints Directly on demo.app with Full CORS
demo.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: Optional[str] = None
    prompt: Optional[str] = None
    session_id: Optional[str] = None
    language: Optional[str] = "ar"
    lang: Optional[str] = None

@demo.app.post("/api/chat")
async def chat_api(req: ChatRequest = Body(...)):
    user_msg = req.message or req.prompt or ""
    user_lang = req.language or req.lang or "ar"
    session_id = req.session_id or str(uuid.uuid4())

    result = answer_student_query(user_msg, language=user_lang)

    return {
        "reply": result["reply"],
        "answer": result["reply"],
        "source_url": result["source_url"],
        "sources": result["sources"],
        "session_id": session_id
    }

@demo.app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Rafeeq Backend API",
        "gemini_online": gemini_client is not None
    }

# 4. Standard Native Gradio Launch (Hugging Face Spaces Native Architecture)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
