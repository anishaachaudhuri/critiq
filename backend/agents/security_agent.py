import json
from backend.orchestrator.state import CritiqState
from backend.core.llm import get_llm
from backend.core.prompts import SECURITY_REVIEW_PROMPT, build_context_block
from backend.schemas.review_schemas import SecurityReview


def security_agent(state: CritiqState) -> dict:
    try:
        llm = get_llm()
        context = build_context_block(state.get("metadata"))
        prompt = SECURITY_REVIEW_PROMPT.format(
            language=state["language"],
            code=state["code"],
            context=context,
        )
        response = llm.invoke(prompt)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return {"reviews": [SecurityReview(**json.loads(raw))]}
    except Exception as e:
        return {"reviews": [SecurityReview(
            issues=[], overall_assessment=f"Agent failed: {e}", score=0
        )]}