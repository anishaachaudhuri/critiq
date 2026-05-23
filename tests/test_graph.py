import pytest
from unittest.mock import patch, MagicMock
import json
from backend.schemas.review_schemas import (
    BugReview, SecurityReview, PerformanceReview,
    ReadabilityReview, BestPracticesReview, AggregatedReport, CodeMetadata,
)


def make_review(cls, score=7):
    return cls(
        issues=[], overall_assessment="All clear.", score=score,
    )


def make_llm_response(agent_name, domain, score=7):
    return json.dumps({
        "agent_name": agent_name,
        "domain":     domain,
        "issues":     [],
        "overall_assessment": "No issues found.",
        "score": score,
    })


def make_aggregator_response():
    return json.dumps({
        "overall_score":         7.0,
        "critical_issues_count": 0,
        "high_issues_count":     0,
        "medium_issues_count":   0,
        "low_issues_count":      0,
        "top_priority_fixes":    ["Keep up good practices"],
        "engineering_summary":   "Code is clean and well-structured.",
    })


class TestGraphIntegration:
    @patch("backend.agents.bug_agent.get_llm")
    @patch("backend.agents.security_agent.get_llm")
    @patch("backend.agents.performance_agent.get_llm")
    @patch("backend.agents.readability_agent.get_llm")
    @patch("backend.agents.best_practices_agent.get_llm")
    @patch("backend.orchestrator.aggregator.get_llm")
    @patch("backend.core.analyzer._get_risk_flags")
    def test_full_pipeline_runs_to_completion(
        self,
        mock_flags,
        mock_agg_llm,
        mock_bp_llm,
        mock_read_llm,
        mock_perf_llm,
        mock_sec_llm,
        mock_bug_llm,
    ):
        def make_mock(response_text):
            m = MagicMock()
            r = MagicMock()
            r.content = response_text
            m.invoke.return_value = r
            return m

        mock_flags.return_value = []
        mock_bug_llm.return_value  = make_mock(make_llm_response("Bug Detection Agent",  "Bug Detection"))
        mock_sec_llm.return_value  = make_mock(make_llm_response("Security Review Agent", "Security"))
        mock_perf_llm.return_value = make_mock(make_llm_response("Performance Review Agent", "Performance"))
        mock_read_llm.return_value = make_mock(make_llm_response("Readability Review Agent", "Readability"))
        mock_bp_llm.return_value   = make_mock(make_llm_response("Best Practices Agent", "Best Practices"))
        mock_agg_llm.return_value  = make_mock(make_aggregator_response())

        from backend.orchestrator.graph import critiq_graph

        initial_state = {
            "code":           "def hello():\n    print('hello')",
            "language":       "python",
            "filename":       "hello.py",
            "active_agents":  [],
            "metadata":       None,
            "reviews":        [],
            "final_report":   None,
            "error":          None,
        }

        result = critiq_graph.invoke(initial_state)

        assert result["final_report"] is not None
        assert isinstance(result["final_report"], AggregatedReport)
        assert len(result["reviews"]) == 5
        assert result["final_report"].overall_score == 7.0

    @patch("backend.agents.bug_agent.get_llm")
    @patch("backend.agents.security_agent.get_llm")
    @patch("backend.agents.performance_agent.get_llm")
    @patch("backend.agents.readability_agent.get_llm")
    @patch("backend.agents.best_practices_agent.get_llm")
    @patch("backend.orchestrator.aggregator.get_llm")
    @patch("backend.core.analyzer._get_risk_flags")
    def test_pipeline_survives_one_agent_failure(
        self,
        mock_flags,
        mock_agg_llm,
        mock_bp_llm,
        mock_read_llm,
        mock_perf_llm,
        mock_sec_llm,
        mock_bug_llm,
    ):
        def make_mock(response_text):
            m = MagicMock()
            r = MagicMock()
            r.content = response_text
            m.invoke.return_value = r
            return m

        mock_flags.return_value    = []
        mock_bug_llm.side_effect   = Exception("LLM timeout")
        mock_sec_llm.return_value  = make_mock(make_llm_response("Security Review Agent", "Security"))
        mock_perf_llm.return_value = make_mock(make_llm_response("Performance Review Agent", "Performance"))
        mock_read_llm.return_value = make_mock(make_llm_response("Readability Review Agent", "Readability"))
        mock_bp_llm.return_value   = make_mock(make_llm_response("Best Practices Agent", "Best Practices"))
        mock_agg_llm.return_value  = make_mock(make_aggregator_response())

        from backend.orchestrator.graph import critiq_graph

        initial_state = {
            "code":          "def hello():\n    print('hello')",
            "language":      "python",
            "filename":      "hello.py",
            "active_agents": [],
            "metadata":      None,
            "reviews":       [],
            "final_report":  None,
            "error":         None,
        }

        result = critiq_graph.invoke(initial_state)
        assert result["final_report"] is not None
        assert len(result["reviews"]) == 5
        failed = [r for r in result["reviews"] if r.score == 0]
        assert len(failed) == 1