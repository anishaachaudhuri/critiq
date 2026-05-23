from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CodeMetadata(BaseModel):
    language: str
    line_count: int
    function_count: int
    imports: List[str]
    has_database_access: bool
    has_network_calls: bool
    has_auth_logic: bool
    has_user_input: bool
    has_crypto: bool
    has_file_io: bool
    complexity_estimate: str
    risk_flags: List[str]


class ReviewIssue(BaseModel):
    severity: Severity
    issue: str
    suggestion: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class AgentReview(BaseModel):
    agent_name: str
    domain: str
    issues: List[ReviewIssue]
    overall_assessment: str
    score: int = Field(ge=0, le=10)


class BugReview(AgentReview):
    agent_name: str = "Bug Detection Agent"
    domain: str = "Bug Detection"


class SecurityReview(AgentReview):
    agent_name: str = "Security Review Agent"
    domain: str = "Security"


class PerformanceReview(AgentReview):
    agent_name: str = "Performance Review Agent"
    domain: str = "Performance"


class ReadabilityReview(AgentReview):
    agent_name: str = "Readability Review Agent"
    domain: str = "Readability"


class BestPracticesReview(AgentReview):
    agent_name: str = "Best Practices Agent"
    domain: str = "Best Practices"


class MergedIssue(BaseModel):
    severity: Severity
    issue: str
    suggestion: str
    flagged_by: List[str]
    confidence: float
    line_number: Optional[int] = None


class AggregatedReport(BaseModel):
    overall_score: float = Field(ge=0, le=10)
    critical_issues_count: int
    high_issues_count: int
    medium_issues_count: int
    low_issues_count: int
    top_priority_fixes: List[str]
    engineering_summary: str
    reviews: List[AgentReview]
    merged_issues: List[MergedIssue] = Field(default_factory=list)
    metadata: Optional[CodeMetadata] = None