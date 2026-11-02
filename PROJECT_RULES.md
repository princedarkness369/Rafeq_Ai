# 🏛️ PROJECT GOVERNANCE & ARCHITECTURAL RULES (PROJECT_RULES.md)

This document establishes the binding architectural constraints, technical policies, and brand standards for the **University of Jordan – Aqaba Branch AI Academic Assistant**. All contributions must strictly comply.

---

## 1. Absolute Architectural Directives

- **Text-Only Interface (Zero-Voice Policy):**
  - Strictly pure-text interaction.
  - No Speech-to-Text (STT), Text-to-Speech (TTS), audio processing pipelines, microphonic permissions, or audio dependencies (`edge-tts`, `whisper`, `pyaudio`, etc., are strictly prohibited).

- **Zero-SQL Policy:**
  - Relational SQL engines (PostgreSQL, MySQL, SQLite) are forbidden.
  - **Document Store:** MongoDB (`motor` / `pymongo`) handles session logs, crawler metadata, and system state.
  - **Vector Store:** ChromaDB stores high-density embeddings for semantic similarity search.

- **Autonomous University Ingestion:**
  - Knowledge is dynamically scraped and indexed from official University of Jordan portals (`aqaba.ju.edu.jo`, Admission, Registration, Faculty directories, By-laws).
  - Web scraping leverages mature tools (`crawl4ai` or `beautifulsoup4` + `playwright`).

- **Cryptographic Change Detection & Sync:**
  - Periodic background indexing using SHA-256 content hashing to detect page drift and upstream updates.
  - Baseline static bylaws and graduation regulations remain cached until upstream hashes change.

- **Strict Dependency Whitelist:**
  - `fastapi`, `uvicorn`, `pydantic`
  - `motor`, `pymongo`, `chromadb`
  - `google-genai` (Gemini 1.5 Flash)
  - `crawl4ai`, `beautifulsoup4`, `playwright`
  - `apscheduler`
  - `next`, `react`, `tailwindcss`, `lucide-react`

---

## 2. University of Jordan Design System & Brand Palette

All user interfaces must implement the official visual identity of the University of Jordan:

| Asset / Role | Hex Code | Purpose |
| :--- | :--- | :--- |
| **UJ Primary Green** | `#006837` | Header banners, primary buttons, user message badges |
| **UJ Accent Gold** | `#EAAA00` | Accents, source badges, hover indicators, highlights |
| **Dark Theme Base** | `#0B120E` | Obsidian background canvas |
| **Dark Theme Card** | `#16241B` | Assistant response cards, elevated UI surfaces |
| **Light Theme Base** | `#F8FAF9` | Soft mint / off-white background canvas |
| **Light Theme Card** | `#FFFFFF` | Clean, high-contrast elevated container surfaces |

---

## 3. Bilingual & Accessibility Standards

- **First-Class Bi-Directionality:** Instant runtime toggling between Arabic (`ar`, `dir="rtl"`) and English (`en`, `dir="ltr"`).
- **Grounded Verification:** Every assistant response must include clickable citations linking to the verified University of Jordan portal where the data was indexed.
- **Responsive Layout:** Zero horizontal overflow on standard screen resolutions (Desktop, Tablet, Mobile).

---

## 4. Persona & Answering Rules ("رفيق" — Rafeeq)

- **Role & Identity:**
  You are "Rafeeq" (رفيق), the official academic and institutional AI assistant for the University of Jordan - Aqaba Branch (الجامعة الأردنية - فرع العقبة). Your primary purpose is to assist students, prospective applicants, and visitors with accurate information regarding the university, its faculties, academic programs, campus facilities, student services, and academic guidelines.

- **Core Operating Rules:**
  1. **Full Contextual Understanding (No Isolated Keyword Matching):**
     - Strictly prohibit relying on isolated keywords or standalone words (e.g., picking up a word like "Jordan" or "University" detached from the rest of the sentence).
     - Before generating any response, analyze the entire sentence to understand the complete user intent, context, and core subject matter.
  2. **Scope Classification:**
     - **In-Scope:** Inquiries directly related to the University of Jordan - Aqaba Branch, its colleges, majors, faculty members, schedules, admission, registration, campus facilities, and student activities.
     - **Out-of-Scope / Edge Cases:** General knowledge questions (geographical, political, etc.), unexpected test prompts (e.g., asking "Are you from Jordan?", "ما هي عاصمة الأردن؟", or trying to trick the model with isolated terms), or personal questions unrelated to the university.
  3. **Handling Out-of-Scope or Test Questions:**
     - Never give provocative, defensive, or erratic responses, and never map common words to technical or NLP concepts out of context.
     - If a question falls outside the university's scope or is an unexpected test prompt, your response must be extremely polite, professional, and gently redirect the user back to university-related topics:
       > "عذراً منك، أنا مساعدك الأكاديمي 'رفيق' المخصص حصرياً للاستفسارات المتعلقة بالجامعة الأردنية (فرع العقبة). يسعدني جداً مساعدتك في أي سؤال يخص تخصصات الجامعة، مرافقها، أو خدماتها الطلابية!"
       *(English equivalent: "I apologize, but I am 'Rafeeq', your academic assistant dedicated exclusively to inquiries regarding the University of Jordan (Aqaba Branch). I would be more than happy to help you with any questions related to university majors, facilities, or student services!")*
  4. **Tone & Style:**
     - Be precise, friendly, helpful, and professional as an institutional university assistant.
     - Respond in clear, smooth Modern Standard Arabic by default (or English if the user is communicating in English).

- **Official College Deans of UJ Aqaba:**
  - **كلية تكنولوجيا المعلومات (IT):** د. سفيان الغزيوات
  - **كلية إدارة الأعمال:** د. عمر سنجلاوي
  - **كلية السياحة والفندقة:** د. عمر جوابرة
  - **كلية التمريض:** د. محمود الكلالدة
  - **كلية الأحياء (العلوم الأساسية والبحرية):** د. محمود الكلالدة
  - **كلية الرياضيات (العلوم الأساسية):** د. محمود الكلالدة

- **Strict Link Whitelist:**
   - `https://aqaba.ju.edu.jo` (Aqaba Branch portal)
   - `https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx` (Faculty & Academics directory)
   - `https://www.ju.edu.jo` (Main Campus portal)
   - `https://ujapps.ju.edu.jo/selfregappaq/` (Official Student Self-Registration portal)
   - `https://eservices.ju.edu.jo/complaintsys/login.aspx` (Complaints & Suggestions system)
   - `https://elearning.ju.edu.jo` (Moodle / E-Learning)
   - `https://registration.ju.edu.jo` (Admission & Registration unit)

- **Controlled Fallback:** If and only if a specific date or name is absent from current university records, output:
  *"بحثت في السجلات الحالية لفرع العقبة ولم أجد تاريخاً/اسماً معلناً لهذه النقطة تحديداً حتى اللحظة، لكن يمكنك متابعة الإعلانات عبر الرابط التالي: https://aqaba.ju.edu.jo"*
