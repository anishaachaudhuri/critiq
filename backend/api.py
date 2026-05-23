import json
import asyncio
import traceback
import zipfile
import io
import os
from typing import Optional, List, AsyncGenerator
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.orchestrator.state import CritiqState
from backend.orchestrator.graph import critiq_graph
from backend.reporting.exporter import save_report, list_reports, load_report
from backend.reporting.html_report import generate_html_report
from backend.core.analyzer import analyze_code

app = FastAPI(title="Critiq API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None


class DiffRequest(BaseModel):
    code_before: str
    code_after: str
    language: str
    filename: Optional[str] = None


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def _run_pipeline(code: str, language: str, filename: Optional[str]) -> AsyncGenerator[str, None]:
    try:
        yield _sse("status", {"message": "Analyzing code structure..."})

        metadata = analyze_code(code, language)
        yield _sse("metadata", metadata.model_dump())

        yield _sse("status", {"message": "Dispatching agents in parallel..."})

        initial_state: CritiqState = {
            "code": code,
            "language": language,
            "filename": filename,
            "active_agents": [],
            "metadata": metadata,
            "reviews": [],
            "final_report": None,
            "error": None,
        }

        for name in ["Bug Detection", "Security", "Performance", "Readability", "Best Practices"]:
            yield _sse("agent_start", {"domain": name})

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: critiq_graph.invoke(initial_state))

        if result.get("error"):
            yield _sse("error", {"message": result["error"]})
            return

        report = result["final_report"]

        for review in report.reviews:
            yield _sse("agent_complete", {
                "domain":             review.domain,
                "score":              review.score,
                "issue_count":        len(review.issues),
                "overall_assessment": review.overall_assessment,
                "issues":             [i.model_dump() for i in review.issues],
            })

        yield _sse("status", {"message": "Aggregating findings..."})

        json_path = save_report(report, filename)
        html_path = generate_html_report(report, filename)

        yield _sse("complete", {
            "overall_score":          report.overall_score,
            "critical_issues_count":  report.critical_issues_count,
            "high_issues_count":      report.high_issues_count,
            "medium_issues_count":    report.medium_issues_count,
            "low_issues_count":       report.low_issues_count,
            "top_priority_fixes":     report.top_priority_fixes,
            "engineering_summary":    report.engineering_summary,
            "merged_issues":          [i.model_dump() for i in report.merged_issues],
            "html_report_path":       html_path,
            "json_report_path":       json_path,
        })

    except Exception as e:
        yield _sse("error", {"message": str(e), "trace": traceback.format_exc()})


@app.post("/review/stream")
async def review_stream(request: ReviewRequest):
    return StreamingResponse(
        _run_pipeline(request.code, request.language, request.filename),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/review/diff")
async def review_diff(request: DiffRequest):
    from backend.reporting.differ import build_diff_context
    diff_context = build_diff_context(request.code_before, request.code_after)
    augmented    = diff_context + "\n" + request.code_after
    return StreamingResponse(
        _run_pipeline(augmented, request.language, request.filename),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


SUPPORTED_EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".go": "go", ".rs": "rust",
    ".cpp": "cpp", ".c": "c", ".rb": "ruby",
}


@app.post("/review/multi")
async def review_multi(file: UploadFile = File(...)):
    contents = await file.read()
    files_to_review = []

    if file.filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(contents)) as zf:
            for name in zf.namelist():
                ext = os.path.splitext(name)[1].lower()
                if ext in SUPPORTED_EXTENSIONS and not name.startswith("__"):
                    try:
                        code = zf.read(name).decode("utf-8", errors="ignore")
                        if code.strip():
                            files_to_review.append((name, code, SUPPORTED_EXTENSIONS[ext]))
                    except Exception:
                        continue
    else:
        ext  = os.path.splitext(file.filename)[1].lower()
        lang = SUPPORTED_EXTENSIONS.get(ext, "python")
        files_to_review.append((file.filename, contents.decode("utf-8", errors="ignore"), lang))

    async def stream():
        all_reports = []
        for fname, code, lang in files_to_review[:10]:
            yield _sse("file_start", {"filename": fname, "language": lang})
            async for event in _run_pipeline(code, lang, fname):
                if event.startswith("event: complete"):
                    yield _sse("file_complete", {"filename": fname})
                yield event
            yield _sse("file_done", {"filename": fname})

        yield _sse("multi_complete", {
            "file_count": len(files_to_review),
            "message":    f"Analyzed {len(files_to_review)} files.",
        })

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/history")
async def get_history():
    reports = []
    for path in list_reports()[:20]:
        try:
            data = load_report(path)
            reports.append({
                "path":         path,
                "filename":     data.get("source_filename", "unknown"),
                "generated_at": data.get("generated_at", ""),
                "overall_score": data.get("overall_score", 0),
                "critical":     data.get("critical_issues_count", 0),
                "high":         data.get("high_issues_count", 0),
                "medium":       data.get("medium_issues_count", 0),
                "low":          data.get("low_issues_count", 0),
            })
        except Exception:
            continue
    return {"reports": reports}


@app.get("/history/{report_id}")
async def get_report(report_id: str):
    from backend.reporting.exporter import REPORTS_DIR
    path = os.path.join(REPORTS_DIR, report_id + ".json")
    if not os.path.exists(path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return load_report(path)


@app.get("/health")
async def health():
    return {"status": "ok"}