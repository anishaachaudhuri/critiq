import pytest
from pydantic import ValidationError
from backend.schemas.review_schemas import (
    ReviewIssue, BugReview, SecurityReview, AggregatedReport,
    Severity, CodeMetadata, MergedIssue
)


def make_issue(**kwargs):
    defaults = {
        "severity": "high",
        "issue": "SQL injection vulnerability",
        "suggestion": "Use parameterized queries",
    }
    return {**defaults, **kwargs}


def make_review(**kwargs):
    defaults = {
        "issues": [make_issue()],
        "overall_assessment": "Code has critical security issues.",
        "score": 3,
    }
    return {**defaults, **kwargs}


class TestReviewIssue:
    def test_valid_issue(self):
        issue = ReviewIssue(**make_issue())
        assert issue.severity == Severity.HIGH
        assert issue.confidence == 1.0

    def test_all_severities(self):
        for sev in ["critical", "high", "medium", "low"]:
            issue = ReviewIssue(**make_issue(severity=sev))
            assert issue.severity.value == sev

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValidationError):
            ReviewIssue(**make_issue(severity="extreme"))

    def test_optional_fields_default_none(self):
        issue = ReviewIssue(**make_issue())
        assert issue.line_number is None
        assert issue.code_snippet is None

    def test_optional_fields_accepted(self):
        issue = ReviewIssue(**make_issue(line_number=42, code_snippet="x = 1"))
        assert issue.line_number == 42
        assert issue.code_snippet == "x = 1"

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            ReviewIssue(**make_issue(confidence=1.5))
        with pytest.raises(ValidationError):
            ReviewIssue(**make_issue(confidence=-0.1))

    def test_confidence_valid_range(self):
        issue = ReviewIssue(**make_issue(confidence=0.85))
        assert issue.confidence == 0.85


class TestAgentReviews:
    def test_bug_review_defaults(self):
        review = BugReview(**make_review())
        assert review.agent_name == "Bug Detection Agent"
        assert review.domain == "Bug Detection"

    def test_security_review_defaults(self):
        review = SecurityReview(**make_review())
        assert review.agent_name == "Security Review Agent"
        assert review.domain == "Security"

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            BugReview(**make_review(score=11))
        with pytest.raises(ValidationError):
            BugReview(**make_review(score=-1))

    def test_score_valid_range(self):
        review = BugReview(**make_review(score=0))
        assert review.score == 0
        review = BugReview(**make_review(score=10))
        assert review.score == 10

    def test_empty_issues_allowed(self):
        review = BugReview(**make_review(issues=[]))
        assert review.issues == []

    def test_multiple_issues(self):
        issues = [make_issue(), make_issue(severity="critical", issue="Hardcoded password")]
        review = BugReview(**make_review(issues=issues))
        assert len(review.issues) == 2


class TestCodeMetadata:
    def test_valid_metadata(self):
        meta = CodeMetadata(
            language="python",
            line_count=50,
            function_count=3,
            imports=["sqlite3", "hashlib"],
            has_database_access=True,
            has_network_calls=False,
            has_auth_logic=False,
            has_user_input=True,
            has_crypto=True,
            has_file_io=False,
            complexity_estimate="medium",
            risk_flags=["string-concatenated SQL query"],
        )
        assert meta.has_database_access is True
        assert meta.line_count == 50

    def test_empty_risk_flags(self):
        meta = CodeMetadata(
            language="python", line_count=10, function_count=1,
            imports=[], has_database_access=False, has_network_calls=False,
            has_auth_logic=False, has_user_input=False, has_crypto=False,
            has_file_io=False, complexity_estimate="low", risk_flags=[],
        )
        assert meta.risk_flags == []


class TestAggregatedReport:
    def test_valid_report(self):
        reviews = [BugReview(**make_review()), SecurityReview(**make_review())]
        report = AggregatedReport(
            overall_score=4.5,
            critical_issues_count=2,
            high_issues_count=3,
            medium_issues_count=1,
            low_issues_count=0,
            top_priority_fixes=["Fix SQL injection", "Remove hardcoded credentials"],
            engineering_summary="Code has multiple critical issues.",
            reviews=reviews,
        )
        assert report.overall_score == 4.5
        assert len(report.reviews) == 2

    def test_score_out_of_range(self):
        with pytest.raises(ValidationError):
            AggregatedReport(
                overall_score=11.0,
                critical_issues_count=0, high_issues_count=0,
                medium_issues_count=0, low_issues_count=0,
                top_priority_fixes=[], engineering_summary="",
                reviews=[],
            )

    def test_merged_issues_default_empty(self):
        reviews = [BugReview(**make_review())]
        report = AggregatedReport(
            overall_score=5.0,
            critical_issues_count=0, high_issues_count=1,
            medium_issues_count=0, low_issues_count=0,
            top_priority_fixes=["Fix something"],
            engineering_summary="Summary here.",
            reviews=reviews,
        )
        assert report.merged_issues == []