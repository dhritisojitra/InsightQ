# 📚 InsightQ

> **AI-powered academic PDF assistant** — Upload documents, ask natural language questions, get cited answers, generate summaries, and create MCQ quizzes.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange?style=flat)](https://www.trychroma.com)
[![Gemini](https://img.shields.io/badge/Gemini-1.5--flash-4285F4?style=flat&logo=google)](https://aistudio.google.com)

---

## ✨ Features

### Frontend
- 🖥️ **Modern responsive dashboard** — glassmorphism UI with dark/light mode
- 📤 **PDF upload with drag & drop** — file validation, circular progress indicator
- 📋 **Document library** — filename, page count, size, upload time
- 💬 **ChatGPT-style Q&A** — real-time conversation per document
- 🔗 **Citation badges** — source filename + page number for every answer
- 💡 **Suggested questions** — auto-generated on upload
- 📝 **Summary panel** — structured summary with key topics
- 🎓 **Interactive MCQ quiz** — generate, answer, and check understanding
- 💾 **Persistent chat history** — survives page refreshes
- 🌗 **Dark/light mode** — with system preference detection

### Backend
- 📄 **PDF extraction** — PyMuPDF with per-page text extraction
- 🔪 **Smart chunking** — sliding-window word-based chunks with metadata
- 🧠 **Embeddings** — `all-MiniLM-L6-v2` via Sentence Transformers (local, free)
- 🗄️ **Vector storage** — ChromaDB with persistent collections per document
- 🔍 **Semantic search** — cosine similarity retrieval
- 🤖 **RAG pipeline** — retrieve → generate → cite
- ✨ **Gemini 1.5 Flash** — free LLM API for answers, summaries, MCQs
- 📖 **Swagger docs** — interactive API explorer at `/docs`
- 🔒 **Error handling** — structured logging with Loguru, CORS, GZip

---

## 🏗️ Project Structure

```
InsightQ/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Pydantic-Settings env config
│   │   ├── routers/
│   │   │   ├── documents.py     # Upload / list / delete
│   │   │   ├── chat.py          # Q&A + chat history
│   │   │   ├── summary.py       # Document summarization
│   │   │   └── mcq.py           # MCQ generation
│   │   ├── services/
│   │   │   ├── pdf_service.py   # PyMuPDF extraction & chunking
│   │   │   ├── embedding_service.py  # Sentence Transformers
│   │   │   ├── vector_store.py  # ChromaDB operations
│   │   │   ├── llm_service.py   # Gemini API prompts
│   │   │   └── rag_service.py   # RAG orchestration
│   │   ├── models/schemas.py    # Pydantic v2 schemas
│   │   └── utils/logger.py      # Loguru logging
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root + routing
│   │   ├── index.css            # Design system
│   │   ├── api/client.js        # Axios API client
│   │   ├── hooks/               # useDocuments, useChat, useTheme
│   │   ├── components/          # Sidebar, Chat, MCQ, Summary, etc.
│   │   └── pages/               # Dashboard, DocumentView, NotFound
│   ├── vite.config.js
│   └── .env.example
│
├── sample_pdfs/
├── .env.example
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Gemini API key](https://aistudio.google.com/) (free tier)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/InsightQ.git
cd InsightQ
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

**`.env` file:**
```env
GEMINI_API_KEY=your_actual_key_here
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173
```

**Start the backend:**
```bash
python run.py
# Backend runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

> **First run note:** The embedding model (`all-MiniLM-L6-v2`) will be downloaded automatically (~90MB). This only happens once.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional — proxy is already configured in vite.config.js)
cp .env.example .env

# Start dev server
npm run dev
# Frontend runs at http://localhost:5173
```

### 4. Open the app

Visit [http://localhost:5173](http://localhost:5173) — upload a PDF and start asking questions!

---

## 📡 API Reference

All endpoints are documented interactively at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/documents/upload` | Upload a PDF |
| `GET` | `/api/documents/` | List all documents |
| `GET` | `/api/documents/{doc_id}` | Get document metadata |
| `DELETE` | `/api/documents/{doc_id}` | Delete document |
| `POST` | `/api/chat/{doc_id}/ask` | Ask a question (RAG) |
| `GET` | `/api/chat/{doc_id}/history` | Get chat history |
| `DELETE` | `/api/chat/{doc_id}/history` | Clear chat history |
| `POST` | `/api/summary/{doc_id}` | Generate summary |
| `GET` | `/api/summary/{doc_id}` | Get cached summary |
| `POST` | `/api/mcq/{doc_id}` | Generate MCQs |

### Example API usage

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@my_paper.pdf"
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/api/chat/{doc_id}/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main findings?"}'
```

**Generate MCQs:**
```bash
curl -X POST http://localhost:8000/api/mcq/{doc_id} \
  -H "Content-Type: application/json" \
  -d '{"num_questions": 5, "difficulty": "medium"}'
```

---

## 🌐 Deployment

### Frontend → Vercel

1. Push the repository to GitHub.
2. Go to [vercel.com](https://vercel.com) → **New Project** → Import from GitHub.
3. Set **Root Directory** to `frontend`.
4. Add environment variable:
   ```
   VITE_API_URL = https://your-backend.onrender.com
   ```
5. Deploy! Vercel auto-detects Vite and sets `npm run build` + `dist/` as output.

### Backend → Render

1. Go to [render.com](https://render.com) → **New Web Service**.
2. Connect your GitHub repo.
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
   - **Environment:** Python 3.11
4. Add environment variables:
   ```
   GEMINI_API_KEY = your_actual_key
   ALLOWED_ORIGINS = https://your-app.vercel.app
   DEBUG = false
   ```
5. **Persistent Disk** (optional but recommended): Mount at `/opt/render/project/src/backend` to persist `uploads/`, `chroma_db/`, and `chat_history/` across deploys.

> **Note on Render free tier:** The embedding model (~90MB) is downloaded on first request. Consider using a paid tier for faster cold starts.

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | **Required.** Get from [aistudio.google.com](https://aistudio.google.com) |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformers model |
| `CHUNK_SIZE` | `500` | Words per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of retrieved chunks for RAG |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated) |
| `DEBUG` | `false` | Enable auto-reload and verbose logging |

---

## 🧪 Testing

```bash
# Backend — verify health
curl http://localhost:8000/health

# Backend — run linting
cd backend
pip install ruff
ruff check app/

# Frontend — type check / lint
cd frontend
npm run lint
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend Framework | React 18 + Vite |
| Routing | React Router v6 |
| HTTP Client | Axios |
| File Upload | react-dropzone |
| Notifications | react-hot-toast |
| Icons | Lucide React |
| Backend Framework | FastAPI 0.111 |
| PDF Parsing | PyMuPDF (fitz) |
| Embeddings | Sentence Transformers `all-MiniLM-L6-v2` |
| Vector Database | ChromaDB 0.5 |
| LLM | Google Gemini 1.5 Flash |
| Logging | Loguru |
| Config | Pydantic-Settings |

---

## 📄 License

MIT © 2024
