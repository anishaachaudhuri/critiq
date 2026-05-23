import os
from typing import Optional, List
from backend.orchestrator.graph import critiq_graph
from backend.orchestrator.state import CritiqState
from backend.schemas.review_schemas import AggregatedReport
from backend.reporting.exporter import save_report
from backend.reporting.html_report import generate_html_report


def run_review(
    code: str,
    language: str,
    filename: Optional[str] = None,
    active_agents: Optional[List[str]] = None,
    save: bool = True,
) -> AggregatedReport:
    initial_state: CritiqState = {
        "code": code,
        "language": language,
        "filename": filename,
        "active_agents": active_agents or [],
        "metadata": None,
        "reviews": [],
        "final_report": None,
        "error": None,
    }
    result = critiq_graph.invoke(initial_state)
    if result.get("error"):
        raise RuntimeError(f"Workflow failed: {result['error']}")

    report = result["final_report"]

    if save:
        json_path = save_report(report, filename)
        html_path = generate_html_report(report, filename)
        print(f"  JSON saved: {json_path}")
        print(f"  HTML saved: {html_path}")

    return report


def diff_review(
    code_before: str,
    code_after: str,
    language: str,
    filename: Optional[str] = None,
) -> AggregatedReport:
    from backend.reporting.differ import build_diff_context
    diff_context = build_diff_context(code_before, code_after)
    augmented_code = diff_context + "\n" + code_after
    return run_review(augmented_code, language, filename)


if __name__ == "__main__":
    import time

    sample = """
import sqlite3, hashlib

password = "admin123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchone()

def find_dupes(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j] and i != j:
                result.append(items[i])
    return result

def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
"""

    print("Running Critiq Phase 4...\n")
    start = time.time()
    report = run_review(sample, "python", "example.py")
    elapsed = time.time() - start

    print(f"\nCompleted in {elapsed:.1f}s")
    if report.metadata:
        m = report.metadata
        print(f"\n=== Code Analysis ===")
        print(f"Lines: {m.line_count} | Functions: {m.function_count} | Complexity: {m.complexity_estimate}")
        print(f"Risk flags: {', '.join(m.risk_flags) if m.risk_flags else 'none'}")

    print(f"\n=== Results ===")
    print(f"Score: {report.overall_score}/10")
    print(f"Critical: {report.critical_issues_count} | High: {report.high_issues_count} | Medium: {report.medium_issues_count} | Low: {report.low_issues_count}")

    print(f"\n=== Merged Issues ({len(report.merged_issues)}) ===")
    for issue in report.merged_issues[:6]:
        print(f"  [{issue.severity.value.upper()}] {issue.issue}")
        print(f"    Agents: {', '.join(issue.flagged_by)} | Confidence: {issue.confidence:.2f}")

    print(f"\n=== Top Priority Fixes ===")
    for i, fix in enumerate(report.top_priority_fixes, 1):
        print(f"  {i}. {fix}")

    print(f"\n=== Engineering Summary ===")
    print(report.engineering_summary)