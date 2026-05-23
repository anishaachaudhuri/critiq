import json
import os
from datetime import datetime
from typing import Optional
from backend.schemas.review_schemas import AggregatedReport

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")


def _ensure_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(report: AggregatedReport, filename: Optional[str] = None) -> str:
    _ensure_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = filename.replace("/", "_").replace(".", "_") if filename else "review"
    report_filename = f"{label}_{timestamp}.json"
    path = os.path.join(REPORTS_DIR, report_filename)

    data = report.model_dump()
    data["generated_at"] = datetime.now().isoformat()
    data["source_filename"] = filename

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return path


def load_report(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def list_reports() -> list:
    _ensure_dir()
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
    files.sort(reverse=True)
    return [os.path.join(REPORTS_DIR, f) for f in files]