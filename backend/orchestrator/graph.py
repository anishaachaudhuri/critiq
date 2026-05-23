from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from backend.orchestrator.state import CritiqState
from backend.orchestrator.aggregator import aggregator_node
from backend.agents.bug_agent import bug_agent
from backend.agents.security_agent import security_agent
from backend.agents.performance_agent import performance_agent
from backend.agents.readability_agent import readability_agent
from backend.agents.best_practices_agent import best_practices_agent
from backend.core.analyzer import analyze_code

AGENT_MAP = {
    "bug_review":            "bug_agent",
    "security_review":       "security_agent",
    "performance_review":    "performance_agent",
    "readability_review":    "readability_agent",
    "best_practices_review": "best_practices_agent",
}


def analyzer_node(state: CritiqState) -> dict:
    metadata = analyze_code(state["code"], state["language"])
    return {"metadata": metadata}


def dispatch(state: CritiqState):
    active = state.get("active_agents") or list(AGENT_MAP.keys())
    return [Send(AGENT_MAP[k], state) for k in active if k in AGENT_MAP]


def build_graph():
    graph = StateGraph(CritiqState)

    graph.add_node("analyzer",             analyzer_node)
    graph.add_node("bug_agent",            bug_agent)
    graph.add_node("security_agent",       security_agent)
    graph.add_node("performance_agent",    performance_agent)
    graph.add_node("readability_agent",    readability_agent)
    graph.add_node("best_practices_agent", best_practices_agent)
    graph.add_node("aggregator",           aggregator_node)

    graph.add_edge(START, "analyzer")
    graph.add_conditional_edges("analyzer", dispatch)

    graph.add_edge("bug_agent",            "aggregator")
    graph.add_edge("security_agent",       "aggregator")
    graph.add_edge("performance_agent",    "aggregator")
    graph.add_edge("readability_agent",    "aggregator")
    graph.add_edge("best_practices_agent", "aggregator")
    graph.add_edge("aggregator",           END)

    return graph.compile()


critiq_graph = build_graph()