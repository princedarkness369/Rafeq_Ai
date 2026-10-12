# 🏛️ PROJECT_BUILD_GUIDE.md - University of Jordan (Aqaba Branch) AI Academic Assistant

## 📁 System Architecture & Directory Layout

```text
rafeq/
├── docker-compose.yml          # Full-stack orchestration (Backend + Frontend)
├── .gitignore                  # Git ignore rules (protects credentials & artifacts)
├── .env.example                # Global environment variables template
├── README.md                   # Project overview & quick start
├── PROJECT_RULES.md            # Institutional rules & architectural guidelines
├── PROJECT_BUILD_GUIDE.md      # Step-by-step setup and verification guide
├── backend/
│   ├── .env.example            # Backend environment template
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container definition
│   └── app/
│       ├── __init__.py
│       ├── config.py           # Settings, seed URLs & domain boundaries
│       ├── main.py             # FastAPI app, lifespan & crawler scheduler
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py       # REST endpoints (/api/chat, /health, /history)
│       │   ├── chat_routes.py
│       │   ├── admin_routes.py
│       │   └── rag_service.py  # Grounded RAG orchestrator & Gemini integration
│       ├── crawler/
│       │   ├── __init__.py
│       │   ├── crawler_service.py # Ingestion engine & CLI runner
│       │   ├── change_detector.py # SHA-256 content hashing & sync
│       │   ├── scraper.py         # Baseline university dataset & scraper
│       │   └── scheduler.py       # APScheduler periodic scanner
│       ├── db/
│       │   ├── __init__.py
│       │   ├── nosql_db.py     # MongoDB & MemoryDocumentStore
│       │   ├── mongo_client.py # Motor asynchronous client
│       │   └── vector_db.py    # ChromaDB persistent vector store
│       └── services/
│           ├── __init__.py
│           ├── db.py           # Document persistence wrapper
│           ├── vector_service.py # Text chunking & similarity search
│           └── agent_service.py  # Intent detection & reasoning engine
└── frontend/
    ├── package.json            # Node scripts
    ├── Dockerfile              # Frontend container
    ├── index.html              # Academic web portal layout
    ├── style.css               # UJ Brand Palette & responsive styles
    ├── app.js                  # Dynamic chat, bilingual RTL/LTR engine
    └── assets/
        ├── uj_logo.png         # University logo mark
        └── uj_building.jpg     # Campus building hero visual
```

---

## ⚙️ Environment Configuration

1. Copy `.env.example` to `backend/.env`:
```bash
# On Linux / macOS:
cp .env.example backend/.env

# On Windows:
Copy-Item .env.example backend/.env
```

2. Configure environment variables in `backend/.env`:
```ini
# Google Gemini API
GEMINI_API_KEY="your-gemini-api-key"
GEMINI_MODEL="gemini-3.8-flash"

# NoSQL & Vector Databases
MONGO_URI="mongodb://localhost:27017"
MONGODB_URI="mongodb://localhost:27017"
MONGO_DB_NAME="uj_academic_assistant"
MONGODB_DB_NAME="uj_academic_assistant"
CHROMA_PERSIST_DIR="./chroma_db"

# Service & Ingestion Settings
CRAWLER_INTERVAL_HOURS="24"
UJ_AQABA_BASE_URL="https://aqaba.ju.edu.jo"
API_PORT=8000
PORT=8000
API_HOST="0.0.0.0"
```

---

## 🛠️ Step-by-Step Backend Setup

1. **Navigate to the Backend Directory:**
```bash
cd backend
```

2. **Initialize and Activate Virtual Environment:**
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Verify Database Dependencies (Optional):**
If Docker Desktop is installed, MongoDB can be started locally:
```bash
docker run -d -p 27017:27017 --name uj-mongo mongo:latest
```
> **Note:** MongoDB is **optional**. If MongoDB is offline, the system automatically uses the built-in zero-config **`MemoryDocumentStore`** and persistent ChromaDB store without any errors.

5. **Run Ingestion & Crawler Test:**
```bash
python -m app.crawler.crawler_service
```

6. **Start the FastAPI Application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation will be accessible at: `http://localhost:8000/docs`

---

## 🎨 Step-by-Step Frontend Setup

1. **Navigate to the Frontend Directory:**
```bash
cd frontend
```

2. **Install Node Dependencies:**
```bash
npm install
```

3. **Run Development Web Server:**
```bash
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## 🐳 Full Stack Deployment (Docker)

To run the entire system with one command:
```bash
docker-compose up --build -d
```
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 🧪 Health Check & Sanity Verification

- **Backend Health:** Send a GET request to `http://localhost:8000/health`. Verify HTTP status 200 with status `"healthy"`.
- **RAG Pipeline Test:** Send a test query to `/api/chat` with `{"message": "متى تبدأ فترة السحب والإضافة؟", "language": "ar"}`.
- **Frontend Verification:** Ensure bi-directional layout toggles smoothly between Arabic (`dir="rtl"`, Cairo font) and English (`dir="ltr"`, Plus Jakarta Sans font) and theme switching works as expected.
