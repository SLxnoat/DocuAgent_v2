# DocuAgent AI — Observe & Generate Engine

> **DocuAgent AI** is an autonomous documentation engine that eliminates manual technical writing and static screenshot drafting. Featuring a live interactive browser recording workspace powered by a multi-agent **LangGraph** execution pipeline, **Playwright CDP** telemetry, and **Ollama Cloud** LLMs.

---

## 🏗️ Architecture Overview

```
                                  DOCUAGENT AI ARCHITECTURE
                                  ==========================

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   REACT FRONTEND (SPA)                                 │
│  ┌─────────────────────────┬─────────────────────────────────┬──────────────────────┐  │
│  │    LEFT CONTROL PANE    │       CENTER WORKSPACE PANE     │   RIGHT CHAT PANE    │  │
│  │                         │                                 │                      │  │
│  │  - URL Setup            │  - Live Embedded Browser        │  - Human-in-the-Loop │  │
│  │  - Auth Credentials     │    (Playwright / CDP Stream)    │    Chatbot           │  │
│  │  - Session Rec Controls │  - Live Markdown Manual Preview │  - Granular Section  │  │
│  │  - One-Click PDF Export │  - Split Canvas View            │    Refinements       │  │
└──┴─────────────────────────┴─────────────────────────────────┴──────────────────────┴──┘
                                              │
                      WebSocket / REST API   │  (DOM Events & Screenshot Streams)
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FASTAPI BACKEND ORCHESTRATOR                             │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                            PLAYWRIGHT RECORDING ENGINE                           │  │
│  │  - Embedded CDP Event Listener (Clicks, Inputs, Navigation, Form Submissions)    │  │
│  │  - Real-time DOM CSS Injection (Outline: 4px solid #ef4444) for UI Highlighting  │  │
│  │  - Dynamic Action-Trace Logger (JSON Schema Generation)                         │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                              │                                         │
│                                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         LANGGRAPH MULTI-AGENT PIPELINE                           │  │
│  │                                                                                  │  │
│  │    [1. Intent Parser Agent] ──> [2. Technical Writer] ──> [3. Quality Reviewer]   │  │
│  │               ▲                                                     │            │  │
│  │               └───────────── [4. Chat Refiner Agent] ───────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                              │                                         │
│                                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                     CELERY + REDIS BACKGROUND WORKER & EXPORT                    │  │
│  │  - Async Document Compilation  |  WeasyPrint / Puppeteer PDF Exporter Engine      │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
DocuAgent_v2/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   └── AGENTS_FLOW.md
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   ├── schemas/
│   │   │   ├── session.py
│   │   │   ├── action_trace.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   ├── engine/
│   │   │   ├── browser_manager.py
│   │   │   ├── cdp_listener.py
│   │   │   ├── dom_highlighter.py
│   │   │   ├── screencast.py
│   │   │   └── action_tracer.py
│   │   ├── agents/
│   │   │   ├── state.py
│   │   │   ├── graph.py
│   │   │   ├── llm_factory.py
│   │   │   ├── prompts/
│   │   │   └── nodes/
│   │   ├── api/
│   │   │   ├── v1/endpoints/
│   │   │   └── websockets/
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks/
│   │   ├── exporter/
│   │   │   ├── pdf_generator.py
│   │   │   └── templates/
│   │   └── storage/
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── store/
        ├── hooks/
        ├── api/
        ├── types/
        └── components/
            ├── layout/
            ├── control-pane/
            ├── workspace-pane/
            └── chat-pane/
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: 3.11+
- **Node.js**: 20+
- **Redis**: 7+ (or run via Docker)

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env and supply your OLLAMA_BASE_URL and OLLAMA_API_KEY
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Launch FastAPI Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Celery Worker (in separate terminal)
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app.celery worker --loglevel=info
```

### 5. Frontend Setup (in separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** to launch DocuAgent AI.

---

## 🐳 Running with Docker Compose

To start the entire cluster (Redis, FastAPI Backend, Celery Worker, React Frontend):
```bash
docker compose up --build
```
