from typing import TypedDict, Optional, List, Annotated
import operator
from backend.schemas.review_schemas import AgentReview, AggregatedReport, CodeMetadata


class CritiqState(TypedDict):
    code: str
    language: str
    filename: Optional[str]
    active_agents: List[str]
    metadata: Optional[CodeMetadata]
    reviews: Annotated[List[AgentReview], operator.add]
    final_report: Optional[AggregatedReport]
    error: Optional[str]