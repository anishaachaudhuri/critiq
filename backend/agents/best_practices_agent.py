import json
from backend.orchestrator.state import CritiqState
from backend.core.llm import get_llm
from backend.core.prompts import BEST_PRACTICES_REVIEW_PROMPT, build_context_block
from backend.schemas.review_schemas import BestPracticesReview


def best_practices_agent(state: CritiqState) -> dict:
    try:
        llm = get_llm()
        context = build_context_block(state.get("metadata"))
        prompt = BEST_PRACTICES_REVIEW_PROMPT.format(
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
        return {"reviews": [BestPracticesReview(**json.loads(raw))]}
    except Exception as e:
        return {"reviews": [BestPracticesReview(
            issues=[], overall_assessment=f"Agent failed: {e}", score=0
        )]}