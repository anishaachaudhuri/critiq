# Critiq — AI Multi-Agent Code Review System

> An orchestrator-controlled agentic AI system that performs intelligent code reviews using five specialized reviewer agents running in parallel.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple?style=flat-square)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?style=flat-square)

---

## What It Does

Critiq analyzes code through a structured multi-agent pipeline and produces a prioritized engineering review covering bugs, security vulnerabilities, performance issues, readability problems, and best practice violations.

It is a finite, deterministic workflow where each agent executes once, returns structured output, and stops. The orchestrator controls everything.

---

## Architecture
```
Code Input
      │
      ▼
Code Analyzer          ← extracts imports, detects risk patterns, estimates complexity
      │
      ▼
LangGraph Orchestrator ← dispatches all agents in parallel via Send API
│
├── Bug Detection Agent
├── Security Review Agent      ← all execute concurrently
├── Performance Review Agent
├── Readability Review Agent
└── Best Practices Agent
    │
    ▼
Aggregator             ← deduplicates findings, computes scores, synthesizes summary
    │
    ▼
AggregatedReport       ← Pydantic-validated structured output
│
├── JSON Export
└── HTML Report
```
Every agent receives structured metadata about the code (imports detected, risk flags, complexity estimate) injected into its prompt before execution. This context-engineering approach produces significantly more accurate findings than naive prompting.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph, Send API, conditional edges) |
| LLM | Groq API — Llama 3.3 70B |
| Structured outputs | Pydantic v2 |
| Backend | FastAPI + Server-Sent Events |
| Frontend | React 18 + Vite + CSS Modules |
| Code highlighting | highlight.js |
| Testing | pytest + pytest-mock |

---

## Features

- **Parallel agent execution** — all five agents run simultaneously via LangGraph's Send API, reducing latency by ~5x versus sequential execution
- **Structured outputs** — every agent returns typed Pydantic models, eliminating hallucination propagation between pipeline stages
- **Pre-analysis context injection** — a dedicated analyzer node extracts code metadata before any agent runs, sharpening each agent's focus
- **Cross-agent deduplication** — the aggregator merges semantically similar findings across agents with confidence scoring
- **Real-time streaming** — FastAPI streams pipeline events to the frontend via SSE as they occur
- **Diff review** — submit before/after versions, agents focus only on what changed
- **Multi-file analysis** — upload a zip or multiple files, each analyzed independently
- **Review history** — every review persisted as JSON, browsable from the UI
- **Export** — HTML report and JSON export after every review

---

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend

```bash
git clone https://github.com/anishaachaudhuri/critiq.git
cd critiq

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# add your GROQ_API_KEY to .env
```

### Frontend

```bash
cd frontend-react
npm install
```

### Run

Terminal 1 — API server:
```bash
cd critiq
source .venv/bin/activate
uvicorn backend.api:app --reload --port 8000
```

Terminal 2 — React frontend:
```bash
cd critiq/frontend-react
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Running Tests

```bash
cd critiq
source .venv/bin/activate
python -m pytest tests/ -v
```

---

## Project Structure
```
critiq/
├── backend/
│   ├── agents/           # Five specialized reviewer agents
│   ├── orchestrator/     # LangGraph graph, state schema, aggregator
│   ├── schemas/          # Pydantic structured output models
│   ├── core/             # LLM client, prompt templates, code analyzer
│   ├── reporting/        # JSON exporter, HTML report generator, differ
│   └── api.py            # FastAPI server with SSE endpoints
├── frontend-react/
│   └── src/
│       └── components/   # React components with CSS modules
├── tests/                # pytest test suite
├── reports/              # Generated review artifacts (gitignored)
└── requirements.txt
```
---

## Demo Video
```
https://github.com/anishaachaudhuri/critiq/blob/main/critiq_demo.mov      
```
Try downloading the video, if file size is too big.

---
