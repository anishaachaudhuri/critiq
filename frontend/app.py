import gradio as gr
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import run_review
from backend.schemas.review_schemas import Severity

SEVERITY_ICONS = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
}

SAMPLE = """import sqlite3, hashlib

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


def fmt_agent(review) -> str:
    if not review:
        return "No data."
    lines = [f"**Score: {review.score}/10**", "", review.overall_assessment, ""]
    for issue in review.issues:
        icon = SEVERITY_ICONS.get(issue.severity, "⚪")
        lines.append(f"{icon} **[{issue.severity.value.upper()}]** {issue.issue}")
        lines.append(f"   → {issue.suggestion}")
        if issue.line_number:
            lines.append(f"   Line {issue.line_number}")
        lines.append("")
    return "\n".join(lines)


def run_critiq(code, language, filename):
    if not code.strip():
        return ("No code submitted.",) + ("",) * 7
    try:
        report = run_review(code, language, filename or None)
        by_domain = {r.domain: r for r in report.reviews}

        score_md = (
            f"## {report.overall_score:.1f} / 10\n\n"
            f"🔴 Critical: {report.critical_issues_count}  "
            f"🟠 High: {report.high_issues_count}  "
            f"🟡 Medium: {report.medium_issues_count}  "
            f"🔵 Low: {report.low_issues_count}"
        )
        priorities_md = "\n\n".join(
            f"**{i}.** {fix}" for i, fix in enumerate(report.top_priority_fixes, 1)
        )

        return (
            score_md,
            priorities_md,
            report.engineering_summary,
            fmt_agent(by_domain.get("Bug Detection")),
            fmt_agent(by_domain.get("Security")),
            fmt_agent(by_domain.get("Performance")),
            fmt_agent(by_domain.get("Readability")),
            fmt_agent(by_domain.get("Best Practices")),
        )
    except Exception as e:
        return (f"**Error:** {e}",) + ("",) * 7


with gr.Blocks(title="Critiq", theme=gr.themes.Soft()) as app:
    gr.Markdown("# ⚡ Critiq — AI Code Review")
    gr.Markdown("*Parallel multi-agent analysis pipeline*")

    with gr.Row():
        with gr.Column(scale=2):
            code_input = gr.Code(label="Code", language="python", value=SAMPLE, lines=22)
            with gr.Row():
                lang = gr.Dropdown(
                    ["python","javascript","typescript","java","go","rust","cpp","c","ruby"],
                    value="python", label="Language", scale=1
                )
                fname = gr.Textbox(label="Filename (optional)", placeholder="main.py", scale=2)
            run_btn = gr.Button("▶  Run Review Pipeline", variant="primary")

        with gr.Column(scale=3):
            score_out = gr.Markdown()
            priorities_out = gr.Markdown()
            summary_out = gr.Markdown()

    gr.Markdown("---\n## Agent Reviews")
    with gr.Tabs():
        with gr.Tab("🐛 Bugs"):            bug_out  = gr.Markdown()
        with gr.Tab("🔒 Security"):        sec_out  = gr.Markdown()
        with gr.Tab("⚡ Performance"):     perf_out = gr.Markdown()
        with gr.Tab("📖 Readability"):     read_out = gr.Markdown()
        with gr.Tab("✅ Best Practices"):  bp_out   = gr.Markdown()

    run_btn.click(
        fn=run_critiq,
        inputs=[code_input, lang, fname],
        outputs=[score_out, priorities_out, summary_out, bug_out, sec_out, perf_out, read_out, bp_out],
    )

if __name__ == "__main__":
    app.launch()