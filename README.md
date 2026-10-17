# 🏛️ University of Jordan (Aqaba Branch) — AI Academic Assistant (رفيق | Rafeq)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![MongoDB](https://img.shields.io/badge/NoSQL-MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-FF6F00?style=flat)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/Governance-UJ%20Aqaba%20Standard-006837?style=flat)](PROJECT_RULES.md)

An institutional, full-stack AI academic website purpose-built for the students, faculty, and administrative community of the **University of Jordan – Aqaba Branch (الجامعة الأردنية – فرع العقبة)**.

---

## 🌟 Key Features & Capabilities

- **🌐 Dedicated Web Platform:** A lightweight, responsive web client accessible from any browser on Desktop, Tablet, and Mobile.
- **🔄 Bilingual & Bi-Directional:** Native runtime switching between Arabic (`RTL`, Cairo font) and English (`LTR`, Plus Jakarta Sans font) with institution-tailored typography.
- **🛡️ Grounded Retrieval-Augmented Generation (RAG):** Responses are strictly synthesized from official University of Jordan web pages using Google Gemini via the official `google-genai` SDK.
- **🔗 Clickable Source Verification:** Every answer links directly to verified university sub-portals (`aqaba.ju.edu.jo`, Registration, Admissions, Faculties).
- **🕷️ Autonomous University Ingestion:**
  - Automated crawler scanning official University of Jordan Aqaba portals.
  - **SHA-256 Cryptographic Hashing** to detect web content drift and trigger atomic vector store updates.
  - Background periodic sync managed via `apscheduler`.
- **🗄️ Zero-SQL Architecture:**
  - **NoSQL Store (MongoDB):** Tracks conversation sessions, audit logs, and crawler hashes (with automatic zero-config memory fallback).
  - **Vector Store (ChromaDB):** Persists dense semantic vector embeddings.
- **⚡ Strict Text-Only Modality:** Zero voice/audio dependencies for maximum privacy, low bandwidth, and fast response times.
- **🎨 University Brand Palette:** Styled with the University of Jordan identity: Heritage Green (`#006837`), Accent Gold (`#EAAA00`), and dark/light themes.

---

## 💻 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.10+) | High-performance asynchronous REST API |
| **LLM Engine** | Google Gemini (`google-genai`) | Gemini Flash models with graceful fallback cascade |
| **Vector Database** | ChromaDB | Local vector store for semantic similarity search |
| **Document Store** | MongoDB (`motor` / `pymongo`) | Session and crawler metadata (with memory fallback) |
| **Web Ingestion** | BeautifulSoup4 + HTTPX + APScheduler | Crawler engine with SHA-256 change detection |
| **Frontend Client** | HTML5, CSS3, Modern JavaScript | Responsive web client with bilingual RTL/LTR support |
| **Containerization** | Docker & Docker Compose | Multi-container setup for backend & frontend |

---

## 📁 Project Structure

```text
rafeq/
├── docker-compose.yml          # Multi-container orchestration
├── .gitignore                  # Git ignore rules (secrets, venv, cache)
├── .env.example                # Environment variables template
├── README.md                   # Project overview & documentation
├── PROJECT_RULES.md            # Institutional governance & rules
├── PROJECT_BUILD_GUIDE.md      # Step-by-step build & verification guide
├── backend/
│   ├── .env.example            # Backend environment template
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container definition
│   └── app/
│       ├── main.py             # FastAPI entrypoint & lifespans
│       ├── config.py           # Pydantic configuration & seed URLs
│       ├── api/                # API route handlers & RAG service
│       ├── crawler/            # Web crawler, SHA-256 detector, scheduler
│       ├── db/                 # MongoDB & ChromaDB vector stores
│       └── services/           # Ingestion, vector, and agent services
└── frontend/
    ├── package.json            # Node scripts & dependencies
    ├── Dockerfile              # Frontend web container
    ├── index.html              # Main web portal template
    ├── style.css               # Design system & responsive styles
    ├── app.js                  # Client logic, bilingual engine, chat UI
    └── assets/                 # Institutional logos & imagery
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Google Gemini API Key** (obtain from [Google AI Studio](https://aistudio.google.com/))
- *(Optional)* **Docker & Docker Compose**

---

### 2. Quick Setup (Local Development)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/rafeq.git
cd rafeq
```

#### Step 2: Configure Environment Variables
Copy `.env.example` to `backend/.env` and add your Gemini API key:
```bash
# On Linux / macOS:
cp .env.example backend/.env

# On Windows (PowerShell):
Copy-Item .env.example backend/.env
```
Open `backend/.env` and configure:
```ini
GEMINI_API_KEY="your-gemini-api-key"
GEMINI_MODEL="gemini-3.8-flash"
PORT=8000
```

#### Step 3: Run the Backend Service
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Linux / macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
> The API will be running at `http://localhost:8000`  
> Interactive Docs: `http://localhost:8000/docs`

#### Step 4: Run the Frontend Website
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
> Open your browser at `http://localhost:3000` to access the website!

---

### 3. Docker Deployment

To launch the complete application stack (Backend + Frontend):

```bash
docker-compose up --build -d
```

- **Frontend Website:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`

To stop the containers:
```bash
docker-compose down
```

---

## 🧪 Verification & Testing

- **Backend Health Check:**
  ```bash
  curl http://localhost:8000/health
  ```
  Expected output: `{"status": "healthy", ...}`

- **Crawler & Ingestion Test:**
  ```bash
  cd backend
  python -m app.crawler.crawler_service
  ```

- **Chat Query Test:**
  ```bash
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"من عميد كلية نظم وتكنولوجيا المعلومات؟\", \"language\": \"ar\"}"
  ```

---

## 🛡️ Institutional Rules & Standards

The project strictly follows institutional governance detailed in [PROJECT_RULES.md](PROJECT_RULES.md):
- **Zero-Audio Policy:** Strictly pure text interface (no audio/voice processing).
- **Zero-SQL Policy:** Relational SQL engines are forbidden. Only MongoDB and ChromaDB are used.
- **Strict Grounding:** Zero unverified assertions. All facts cite verified University of Jordan portals.

---

## 📄 License

Developed for the **University of Jordan – Aqaba Branch**. All institutional assets, logos, and marks remain property of the University of Jordan.


## 📬 Contact

**NAME**

*   LinkedIn: https://www.linkedin.com/in/shahd-al-rabaya-58b8882b1/
*   GitHub: https://github.com/princedarkness369/
*   Email: Shahdfalrabaya@gmail.com

