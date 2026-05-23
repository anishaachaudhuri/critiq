import difflib
from typing import Tuple


def compute_diff(code_before: str, code_after: str) -> Tuple[str, list]:
    before_lines = code_before.splitlines(keepends=True)
    after_lines = code_after.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile="before",
        tofile="after",
        lineterm="",
    ))

    changed_line_numbers = []
    current_line = 0
    for line in diff:
        if line.startswith("@@"):
            parts = line.split("+")
            if len(parts) > 1:
                try:
                    current_line = int(parts[1].split(",")[0])
                except ValueError:
                    pass
        elif line.startswith("+") and not line.startswith("+++"):
            changed_line_numbers.append(current_line)
            current_line += 1
        elif not line.startswith("-"):
            current_line += 1

    diff_text = "".join(diff)
    return diff_text, changed_line_numbers


def build_diff_context(code_before: str, code_after: str) -> str:
    diff_text, changed_lines = compute_diff(code_before, code_after)

    if not diff_text.strip():
        return "No changes detected between the two versions."

    return f"""
DIFF REVIEW MODE:
The following diff shows what changed between the previous and current version.
Focus your review on the added/modified lines (lines starting with +).
Changed line numbers in new version: {changed_lines[:20]}

DIFF:
{diff_text[:3000]}

FULL CODE (current version):
"""