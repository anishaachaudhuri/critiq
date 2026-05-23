import pytest
from unittest.mock import patch, MagicMock
import json
from backend.schemas.review_schemas import (
    BugReview, SecurityReview, Severity, ReviewIssue
)


def make_review(domain, score=6, issues=None):
    classes = {
        "Bug Detection": BugReview,
        "Security":      SecurityReview,
    }
    cls = classes.get(domain, BugReview)
    return cls(
        issues=issues or [],
        overall_assessment=f"{domain} assessment.",
        score=score,
    )


def make_issue(severity="high", issue_text="Test issue", suggestion="Fix it", confidence=1.0):
    return ReviewIssue(severity=severity, issue=issue_text, suggestion=suggestion, confidence=confidence)


def make_state_with_reviews(reviews):
    return {
        "code": "x = 1",
        "language": "python",
        "filename": "test.py",
        "active_agents": [],
        "metadata": None,
        "reviews": reviews,
        "final_report": None,
        "error": None,
    }


class TestDeduplication:
    def test_same_issue_across_agents_merged(self):
        from backend.orchestrator.aggregator import _deduplicate

        issue_text = "No error handling in database calls"
        r1 = make_review("Bug Detection", issues=[make_issue(issue_text=issue_text)])
        r2 = make_review("Security",      issues=[make_issue(issue_text=issue_text)])

        merged = _deduplicate([r1, r2])
        texts = [m.issue for m in merged]
        assert any(issue_text[:30] in t for t in texts)
        multi = [m for m in merged if len(m.flagged_by) > 1]
        assert len(multi) > 0

    def test_different_issues_not_merged(self):
        from backend.orchestrator.aggregator import _deduplicate

        r1 = make_review("Bug Detection", issues=[make_issue(issue_text="SQL injection risk present in query")])
        r2 = make_review("Security",      issues=[make_issue(issue_text="Hardcoded API key detected in source")])

        merged = _deduplicate([r1, r2])
        assert len(merged) == 2

    def test_empty_reviews_returns_empty(self):
        from backend.orchestrator.aggregator import _deduplicate
        assert _deduplicate([]) == []

    def test_confidence_boosted_for_duplicate(self):
        from backend.orchestrator.aggregator import _deduplicate

        issue_text = "Missing input validation on all user data"
        r1 = make_review("Bug Detection", issues=[make_issue(issue_text=issue_text, confidence=0.7)])
        r2 = make_review("Security",      issues=[make_issue(issue_text=issue_text, confidence=0.7)])

        merged = _deduplicate([r1, r2])
        multi = [m for m in merged if len(m.flagged_by) > 1]
        assert len(multi) > 0
        assert multi[0].confidence > 0.7

    def test_sorted_by_severity(self):
        from backend.orchestrator.aggregator import _deduplicate

        r = make_review("Bug Detection", issues=[
            make_issue(severity="low",      issue_text="Minor style issue in naming conventions"),
            make_issue(severity="critical", issue_text="Remote code execution vulnerability found"),
            make_issue(severity="medium",   issue_text="Inefficient loop structure detected here"),
        ])
        merged = _deduplicate([r])
        assert merged[0].severity == Severity.CRITICAL


class TestSeverityCounting:
    def test_counts_correctly(self):
        from backend.orchestrator.aggregator import _count_by_severity

        reviews = [
            make_review("Bug Detection", issues=[
                make_issue(severity="critical"),
                make_issue(severity="high"),
            ]),
            make_review("Security", issues=[
                make_issue(severity="critical"),
                make_issue(severity="medium"),
                make_issue(severity="low"),
            ]),
        ]
        counts = _count_by_severity(reviews)
        assert counts[Severity.CRITICAL] == 2
        assert counts[Severity.HIGH]     == 1
        assert counts[Severity.MEDIUM]   == 1
        assert counts[Severity.LOW]      == 1

    def test_zero_counts_for_empty(self):
        from backend.orchestrator.aggregator import _count_by_severity
        counts = _count_by_severity([])
        assert all(v == 0 for v in counts.values())


class TestAggregatorNode:
    @patch("backend.orchestrator.aggregator.get_llm")
    def test_aggregator_returns_report(self, mock_get_llm):
        mock_resp         = MagicMock()
        mock_resp.content = json.dumps({
            "overall_score":          5.5,
            "critical_issues_count":  1,
            "high_issues_count":      1,
            "medium_issues_count":    0,
            "low_issues_count":       0,
            "top_priority_fixes":     ["Fix SQL injection", "Remove hardcoded password"],
            "engineering_summary":    "The code has serious security issues.",
        })
        mock_llm        = MagicMock()
        mock_llm.invoke.return_value = mock_resp
        mock_get_llm.return_value    = mock_llm

        reviews = [
            make_review("Bug Detection", issues=[make_issue(severity="critical")]),
            make_review("Security",      issues=[make_issue(severity="high")]),
        ]
        from backend.orchestrator.aggregator import aggregator_node
        result = aggregator_node(make_state_with_reviews(reviews))

        assert "final_report" in result
        assert result["final_report"].overall_score == 5.5
        assert len(result["final_report"].reviews) == 2

    @patch("backend.orchestrator.aggregator.get_llm")
    def test_aggregator_handles_empty_reviews(self, mock_get_llm):
        from backend.orchestrator.aggregator import aggregator_node
        result = aggregator_node(make_state_with_reviews([]))
        assert result["final_report"].overall_score == 0.0
        assert result["final_report"].engineering_summary == "Pipeline produced no output."