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
