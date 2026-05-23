import json
from backend.orchestrator.state import CritiqState
from backend.core.llm import get_llm
from backend.core.prompts import AGGREGATION_PROMPT
from backend.schemas.review_schemas import (
    AggregatedReport, MergedIssue, Severity
)


def _count_by_severity(reviews):
    counts = {s: 0 for s in Severity}
    for review in reviews:
        for issue in review.issues:
            counts[issue.severity] += 1
    return counts


def _deduplicate(reviews) -> list:
    seen = {}
    for review in reviews:
        for issue in review.issues:
            key = issue.issue.lower()[:60]
            if key in seen:
                seen[key]["flagged_by"].append(review.domain)
                seen[key]["confidence"] = min(1.0, seen[key]["confidence"] + 0.15)
            else:
                seen[key] = {
                    "severity": issue.severity,
                    "issue": issue.issue,
                    "suggestion": issue.suggestion,
                    "flagged_by": [review.domain],
                    "confidence": issue.confidence,
                    "line_number": issue.line_number,
                }

    merged = []
    for data in seen.values():
        merged.append(MergedIssue(**data))

    merged.sort(
        key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity.value],
            -x.confidence,
        )
    )
    return merged


def aggregator_node(state: CritiqState) -> dict:
    reviews = state.get("reviews") or []

    if not reviews:
        return {"final_report": AggregatedReport(
            overall_score=0.0,
            critical_issues_count=0,
            high_issues_count=0,
            medium_issues_count=0,
            low_issues_count=0,
            top_priority_fixes=["No reviews completed."],
            engineering_summary="Pipeline produced no output.",
            reviews=[],
            merged_issues=[],
        )}

    counts = _count_by_severity(reviews)
    merged = _deduplicate(reviews)

    reviews_json = json.dumps([r.model_dump() for r in reviews], indent=2)

    llm = get_llm()
    prompt = AGGREGATION_PROMPT.format(
        reviews_json=reviews_json,
        critical_count=counts[Severity.CRITICAL],
        high_count=counts[Severity.HIGH],
        medium_count=counts[Severity.MEDIUM],
        low_count=counts[Severity.LOW],
    )
    response = llm.invoke(prompt)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    parsed = json.loads(raw)
    parsed["reviews"] = reviews
    parsed["merged_issues"] = merged
    parsed["metadata"] = state.get("metadata")

    return {"final_report": AggregatedReport(**parsed)}