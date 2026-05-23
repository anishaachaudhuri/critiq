import pytest
import json
from unittest.mock import patch, MagicMock
from backend.schemas.review_schemas import (
    BugReview, SecurityReview, PerformanceReview,
    ReadabilityReview, BestPracticesReview, CodeMetadata,
)


def make_state(code="x = 1", language="python"):
    return {
        "code": code,
        "language": language,
        "filename": "test.py",
        "active_agents": [],
        "metadata": CodeMetadata(
            language=language, line_count=1, function_count=0,
            imports=[], has_database_access=False, has_network_calls=False,
            has_auth_logic=False, has_user_input=False, has_crypto=False,
            has_file_io=False, complexity_estimate="low", risk_flags=[],
        ),
        "reviews": [],
        "final_report": None,
        "error": None,
    }


def make_llm_response(domain, agent_name, score=7):
    return json.dumps({
        "agent_name": agent_name,
        "domain": domain,
        "issues": [
            {
                "severity": "high",
                "issue": "Test issue found",
                "suggestion": "Fix it like this",
                "line_number": 1,
                "code_snippet": "x = 1",
                "confidence": 0.9,
            }
        ],
        "overall_assessment": "Code has one issue.",
        "score": score,
    })


def mock_llm_invoke(response_text):
    mock_llm    = MagicMock()
    mock_resp   = MagicMock()
    mock_resp.content = response_text
    mock_llm.invoke.return_value = mock_resp
    return mock_llm


class TestBugAgent:
    @patch("backend.agents.bug_agent.get_llm")
    def test_returns_bug_review(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Bug Detection", "Bug Detection Agent")
        )
        from backend.agents.bug_agent import bug_agent
        result = bug_agent(make_state())
        assert "reviews" in result
        assert len(result["reviews"]) == 1
        assert isinstance(result["reviews"][0], BugReview)

    @patch("backend.agents.bug_agent.get_llm")
    def test_returns_fallback_on_llm_error(self, mock_get_llm):
        mock_get_llm.side_effect = Exception("LLM unavailable")
        from backend.agents.bug_agent import bug_agent
        result = bug_agent(make_state())
        assert "reviews" in result
        assert result["reviews"][0].score == 0
        assert result["reviews"][0].issues == []

    @patch("backend.agents.bug_agent.get_llm")
    def test_returns_fallback_on_invalid_json(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke("not valid json at all")
        from backend.agents.bug_agent import bug_agent
        result = bug_agent(make_state())
        assert result["reviews"][0].score == 0

    @patch("backend.agents.bug_agent.get_llm")
    def test_strips_markdown_fences(self, mock_get_llm):
        raw = "```json\n" + make_llm_response("Bug Detection", "Bug Detection Agent") + "\n```"
        mock_get_llm.return_value = mock_llm_invoke(raw)
        from backend.agents.bug_agent import bug_agent
        result = bug_agent(make_state())
        assert isinstance(result["reviews"][0], BugReview)

    @patch("backend.agents.bug_agent.get_llm")
    def test_issue_severity_parsed_correctly(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Bug Detection", "Bug Detection Agent")
        )
        from backend.agents.bug_agent import bug_agent
        result = bug_agent(make_state())
        assert result["reviews"][0].issues[0].severity.value == "high"


class TestSecurityAgent:
    @patch("backend.agents.security_agent.get_llm")
    def test_returns_security_review(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Security", "Security Review Agent")
        )
        from backend.agents.security_agent import security_agent
        result = security_agent(make_state())
        assert isinstance(result["reviews"][0], SecurityReview)

    @patch("backend.agents.security_agent.get_llm")
    def test_returns_fallback_on_error(self, mock_get_llm):
        mock_get_llm.side_effect = Exception("timeout")
        from backend.agents.security_agent import security_agent
        result = security_agent(make_state())
        assert result["reviews"][0].score == 0


class TestPerformanceAgent:
    @patch("backend.agents.performance_agent.get_llm")
    def test_returns_performance_review(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Performance", "Performance Review Agent")
        )
        from backend.agents.performance_agent import performance_agent
        result = performance_agent(make_state())
        assert isinstance(result["reviews"][0], PerformanceReview)


class TestReadabilityAgent:
    @patch("backend.agents.readability_agent.get_llm")
    def test_returns_readability_review(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Readability", "Readability Review Agent")
        )
        from backend.agents.readability_agent import readability_agent
        result = readability_agent(make_state())
        assert isinstance(result["reviews"][0], ReadabilityReview)


class TestBestPracticesAgent:
    @patch("backend.agents.best_practices_agent.get_llm")
    def test_returns_best_practices_review(self, mock_get_llm):
        mock_get_llm.return_value = mock_llm_invoke(
            make_llm_response("Best Practices", "Best Practices Agent")
        )
        from backend.agents.best_practices_agent import best_practices_agent
        result = best_practices_agent(make_state())
        assert isinstance(result["reviews"][0], BestPracticesReview)