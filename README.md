# Critiq — AI Code Review Assistant

An orchestrator-controlled agentic AI system for intelligent code review using LangGraph and Groq.

## Architecture

Critiq uses a finite LangGraph workflow where five specialized reviewer agents execute sequentially, each returning structured Pydantic output. An aggregator node synthesizes all findings into a prioritized engineering report.

```
Code Input → Orchestrator → [Bug | Security | Performance | Readability | Best Practices] → Aggregator → Report
```

**Core design principles:**
- Each agent executes once and returns structured output
- Shared typed state flows through the graph (no agent-to-agent communication)
- Explicit graph edges define control flow (no self-routing agents)
- Pydantic models enforce output contracts at runtime

## Stack

- **Orchestration**: LangGraph
- **LLM**: Groq (Llama 3.3 70B)
- **Structured outputs**: Pydantic v2
- **UI**: Gradio
- **Runtime**: Python 3.11+

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
GROQ_API_KEY=your_key_here
```

## Running

**Backend only:**
```bash
python -m backend.main
```

**Full UI:**
```bash
python frontend/app.py
```

## Project Structure

```
critiq/
├── backend/
│   ├── agents/          # Five specialized reviewer agents
│   ├── orchestrator/    # LangGraph workflow graph + state + aggregator
│   ├── schemas/         # Pydantic structured output models
│   ├── core/            # LLM client + prompt templates
│   └── main.py          # Public API entry point
├── frontend/
│   └── app.py           # Gradio UI
└── tests/
```

## Phases

- [x] Phase 1 — Core orchestration pipeline + 5 agents + Gradio UI
- [ ] Phase 2 — Parallel agent execution + LangGraph advanced patterns
- [ ] Phase 3 — Scoring refinement + issue deduplication
- [ ] Phase 4 — Advanced reporting + export
- [ ] Phase 5 — Polished React frontend + real-time workflow visualization
- [ ] Phase 6 — Repository-wide analysis + PR simulation