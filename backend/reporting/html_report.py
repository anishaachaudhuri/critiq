import os
from datetime import datetime
from typing import Optional
from backend.schemas.review_schemas import AggregatedReport, Severity

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")

SEVERITY_COLORS = {
    Severity.CRITICAL: "#ff4444",
    Severity.HIGH:     "#ff8800",
    Severity.MEDIUM:   "#ffcc00",
    Severity.LOW:      "#4488ff",
}

SEVERITY_BG = {
    Severity.CRITICAL: "#2a0a0a",
    Severity.HIGH:     "#2a1500",
    Severity.MEDIUM:   "#1a1a00",
    Severity.LOW:      "#0a0a2a",
}


def _severity_badge(severity: Severity) -> str:
    color = SEVERITY_COLORS[severity]
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
        f'padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;'
        f'letter-spacing:0.5px">{severity.value.upper()}</span>'
    )


def _score_color(score: int) -> str:
    if score >= 8:
        return "#22cc44"
    elif score >= 5:
        return "#ffcc00"
    return "#ff4444"


def _build_css() -> str:
    return """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: #0d0d0d;
        color: #c8c8c8;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
        line-height: 1.6;
    }
    .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
    .header {
        border-bottom: 1px solid #222;
        padding-bottom: 24px;
        margin-bottom: 32px;
    }
    .header h1 {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.3px;
    }
    .header .meta {
        color: #555;
        font-size: 12px;
        margin-top: 6px;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .score-bar {
        display: flex;
        align-items: center;
        gap: 24px;
        background: #111;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .score-number {
        font-size: 48px;
        font-weight: 700;
        line-height: 1;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .score-label { color: #555; font-size: 12px; margin-top: 4px; }
    .severity-counts {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    .severity-count {
        text-align: center;
        padding: 8px 16px;
        border-radius: 6px;
        border: 1px solid #222;
    }
    .severity-count .num {
        font-size: 24px;
        font-weight: 700;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .severity-count .label { font-size: 11px; color: #555; margin-top: 2px; }
    .section {
        margin-bottom: 32px;
    }
    .section-title {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        color: #555;
        text-transform: uppercase;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1a1a1a;
    }
    .summary-box {
        background: #111;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 20px;
        color: #aaa;
        line-height: 1.8;
    }
    .priority-list {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .priority-item {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        background: #111;
        border: 1px solid #222;
        border-radius: 6px;
        padding: 12px 16px;
    }
    .priority-num {
        color: #444;
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 12px;
        min-width: 20px;
        margin-top: 2px;
    }
    .agent-card {
        background: #111;
        border: 1px solid #222;
        border-radius: 8px;
        margin-bottom: 16px;
        overflow: hidden;
    }
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        border-bottom: 1px solid #1a1a1a;
        background: #0f0f0f;
    }
    .agent-name { font-weight: 600; color: #e0e0e0; font-size: 13px; }
    .agent-score {
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 13px;
        font-weight: 700;
    }
    .agent-assessment {
        padding: 14px 20px;
        color: #777;
        font-size: 13px;
        border-bottom: 1px solid #1a1a1a;
    }
    .issue-list { padding: 0; }
    .issue-item {
        padding: 14px 20px;
        border-bottom: 1px solid #161616;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .issue-item:last-child { border-bottom: none; }
    .issue-top {
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .issue-text { color: #c8c8c8; flex: 1; font-size: 13px; }
    .issue-suggestion {
        color: #555;
        font-size: 12px;
        padding-left: 4px;
    }
    .issue-suggestion::before { content: "→ "; color: #333; }
    .issue-meta {
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 11px;
        color: #333;
    }
    .code-snippet {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        padding: 8px 12px;
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 12px;
        color: #666;
        margin-top: 4px;
        overflow-x: auto;
    }
    .metadata-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px;
    }
    .metadata-item {
        background: #111;
        border: 1px solid #222;
        border-radius: 6px;
        padding: 10px 14px;
    }
    .metadata-key { font-size: 11px; color: #444; margin-bottom: 3px; }
    .metadata-value { font-size: 13px; color: #aaa; font-family: 'SF Mono', 'Fira Code', monospace; }
    .flag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .flag {
        background: #1a0a0a;
        border: 1px solid #ff444422;
        color: #ff6666;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .merged-issue {
        background: #111;
        border: 1px solid #222;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 8px;
    }
    .merged-top {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 6px;
    }
    .merged-agents {
        font-size: 11px;
        color: #444;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .confidence-bar-wrap {
        height: 3px;
        background: #1a1a1a;
        border-radius: 2px;
        margin-top: 8px;
    }
    .confidence-bar {
        height: 3px;
        border-radius: 2px;
        background: #334;
    }
    """


def _build_metadata_section(metadata) -> str:
    if not metadata:
        return ""

    flags_html = ""
    if metadata.risk_flags:
        flags = "".join(f'<span class="flag">{f}</span>' for f in metadata.risk_flags)
        flags_html = f'<div class="flag-list">{flags}</div>'

    booleans = {
        "Database access": metadata.has_database_access,
        "Network calls":   metadata.has_network_calls,
        "Auth logic":      metadata.has_auth_logic,
        "User input":      metadata.has_user_input,
        "Crypto ops":      metadata.has_crypto,
        "File I/O":        metadata.has_file_io,
    }

    items = "".join(
        f'<div class="metadata-item">'
        f'<div class="metadata-key">{k}</div>'
        f'<div class="metadata-value" style="color:{"#22cc44" if v else "#444"}">'
        f'{"yes" if v else "no"}</div></div>'
        for k, v in booleans.items()
    )
    items += (
        f'<div class="metadata-item"><div class="metadata-key">Lines</div>'
        f'<div class="metadata-value">{metadata.line_count}</div></div>'
        f'<div class="metadata-item"><div class="metadata-key">Functions</div>'
        f'<div class="metadata-value">{metadata.function_count}</div></div>'
        f'<div class="metadata-item"><div class="metadata-key">Complexity</div>'
        f'<div class="metadata-value">{metadata.complexity_estimate}</div></div>'
    )

    return f"""
    <div class="section">
        <div class="section-title">Code Analysis</div>
        <div class="metadata-grid">{items}</div>
        {"<div class='section-title' style='margin-top:16px'>Risk Flags</div>" + flags_html if flags_html else ""}
    </div>
    """


def _build_merged_issues(merged_issues) -> str:
    if not merged_issues:
        return ""

    items = ""
    for issue in merged_issues:
        color = SEVERITY_COLORS.get(issue.severity, "#888")
        agents = " · ".join(issue.flagged_by)
        conf_pct = int(issue.confidence * 100)
        items += f"""
        <div class="merged-issue">
            <div class="merged-top">
                {_severity_badge(issue.severity)}
                <span class="issue-text">{issue.issue}</span>
            </div>
            <div class="issue-suggestion">{issue.suggestion}</div>
            <div class="merged-agents">flagged by: {agents}</div>
            <div class="confidence-bar-wrap">
                <div class="confidence-bar" style="width:{conf_pct}%;background:{color}66"></div>
            </div>
        </div>
        """

    return f"""
    <div class="section">
        <div class="section-title">Deduplicated Issues ({len(merged_issues)})</div>
        {items}
    </div>
    """


def _build_agent_sections(reviews) -> str:
    html = ""
    for review in reviews:
        score_color = _score_color(review.score)
        issues_html = ""
        for issue in review.issues:
            snippet = (
                f'<div class="code-snippet">{issue.code_snippet}</div>'
                if issue.code_snippet else ""
            )
            line = (
                f'<span class="issue-meta">line {issue.line_number}</span>'
                if issue.line_number else ""
            )
            issues_html += f"""
            <div class="issue-item">
                <div class="issue-top">
                    {_severity_badge(issue.severity)}
                    <span class="issue-text">{issue.issue}</span>
                    {line}
                </div>
                <div class="issue-suggestion">{issue.suggestion}</div>
                {snippet}
            </div>
            """

        no_issues = (
            '<div style="padding:14px 20px;color:#333;font-size:13px">No issues found.</div>'
            if not review.issues else ""
        )

        html += f"""
        <div class="agent-card">
            <div class="agent-header">
                <span class="agent-name">{review.domain}</span>
                <span class="agent-score" style="color:{score_color}">{review.score}/10</span>
            </div>
            <div class="agent-assessment">{review.overall_assessment}</div>
            <div class="issue-list">{issues_html}{no_issues}</div>
        </div>
        """
    return html


def generate_html_report(
    report: AggregatedReport,
    filename: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not output_path:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = filename.replace("/", "_").replace(".", "_") if filename else "review"
        output_path = os.path.join(REPORTS_DIR, f"{label}_{timestamp}.html")

    score_color = _score_color(int(report.overall_score))
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    priorities_html = "".join(
        f'<li class="priority-item">'
        f'<span class="priority-num">{i:02d}</span>'
        f'<span>{fix}</span></li>'
        for i, fix in enumerate(report.top_priority_fixes, 1)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Critiq — {filename or "Code Review"}</title>
<style>{_build_css()}</style>
</head>
<body>
<div class="container">

    <div class="header">
        <h1>⚡ Critiq Code Review</h1>
        <div class="meta">{filename or "unnamed"} · {generated_at}</div>
    </div>

    <div class="score-bar">
        <div>
            <div class="score-number" style="color:{score_color}">{report.overall_score:.1f}</div>
            <div class="score-label">overall score / 10</div>
        </div>
        <div class="severity-counts">
            <div class="severity-count">
                <div class="num" style="color:#ff4444">{report.critical_issues_count}</div>
                <div class="label">Critical</div>
            </div>
            <div class="severity-count">
                <div class="num" style="color:#ff8800">{report.high_issues_count}</div>
                <div class="label">High</div>
            </div>
            <div class="severity-count">
                <div class="num" style="color:#ffcc00">{report.medium_issues_count}</div>
                <div class="label">Medium</div>
            </div>
            <div class="severity-count">
                <div class="num" style="color:#4488ff">{report.low_issues_count}</div>
                <div class="label">Low</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Engineering Summary</div>
        <div class="summary-box">{report.engineering_summary}</div>
    </div>

    <div class="section">
        <div class="section-title">Priority Action Items</div>
        <ul class="priority-list">{priorities_html}</ul>
    </div>

    {_build_metadata_section(report.metadata)}
    {_build_merged_issues(report.merged_issues)}

    <div class="section">
        <div class="section-title">Agent Reviews</div>
        {_build_agent_sections(report.reviews)}
    </div>

</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    return output_path