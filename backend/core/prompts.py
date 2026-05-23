def build_context_block(metadata) -> str:
    if not metadata:
        return ""
    flags = "\n".join(f"  - {f}" for f in metadata.risk_flags) if metadata.risk_flags else "  - none detected"
    return f"""
CODE CONTEXT (pre-analyzed):
- Language: {metadata.language}
- Lines: {metadata.line_count} | Functions: {metadata.function_count} | Complexity: {metadata.complexity_estimate}
- Imports: {", ".join(metadata.imports) if metadata.imports else "none"}
- Database access: {metadata.has_database_access}
- Network calls: {metadata.has_network_calls}
- Auth/credential logic: {metadata.has_auth_logic}
- User input handling: {metadata.has_user_input}
- Cryptographic operations: {metadata.has_crypto}
- File I/O: {metadata.has_file_io}
- Risk flags:
{flags}
"""


BUG_REVIEW_PROMPT = """You are a senior software engineer specializing in bug detection.

{context}

Analyze the following {language} code for bugs, logic errors, edge cases, null pointer risks,
off-by-one errors, unhandled exceptions, and runtime failures.
Pay special attention to the risk flags and context above when they are relevant to bug sources.

CODE:
```{language}
{code}
```

Return a JSON object with exactly this structure:
{{
  "agent_name": "Bug Detection Agent",
  "domain": "Bug Detection",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "Description of the bug",
      "suggestion": "Specific fix",
      "line_number": <integer or null>,
      "code_snippet": "<snippet or null>",
      "confidence": <float 0.0-1.0>
    }}
  ],
  "overall_assessment": "One paragraph summary",
  "score": <integer 0-10>
}}

Return ONLY the JSON. No preamble, no markdown fences."""


SECURITY_REVIEW_PROMPT = """You are a senior application security engineer.

{context}

Analyze the following {language} code for security vulnerabilities.
Focus especially on: injection attacks, hardcoded credentials, insecure crypto,
authentication flaws, sensitive data exposure, and OWASP Top 10.
The context above tells you exactly what sensitive operations this code performs — use it.

CODE:
```{language}
{code}
```

Return a JSON object with exactly this structure:
{{
  "agent_name": "Security Review Agent",
  "domain": "Security",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "Description of the vulnerability",
      "suggestion": "Specific remediation",
      "line_number": <integer or null>,
      "code_snippet": "<snippet or null>",
      "confidence": <float 0.0-1.0>
    }}
  ],
  "overall_assessment": "One paragraph summary",
  "score": <integer 0-10>
}}

Return ONLY the JSON. No preamble, no markdown fences."""


PERFORMANCE_REVIEW_PROMPT = """You are a senior performance engineer.

{context}

Analyze the following {language} code for performance issues.
Focus on: algorithmic complexity, unnecessary loops, redundant computation,
memory inefficiency, blocking operations, and scalability problems.
Use the complexity estimate and import context above to guide your analysis.

CODE:
```{language}
{code}
```

Return a JSON object with exactly this structure:
{{
  "agent_name": "Performance Review Agent",
  "domain": "Performance",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "Description of the performance problem",
      "suggestion": "Specific optimization",
      "line_number": <integer or null>,
      "code_snippet": "<snippet or null>",
      "confidence": <float 0.0-1.0>
    }}
  ],
  "overall_assessment": "One paragraph summary",
  "score": <integer 0-10>
}}

Return ONLY the JSON. No preamble, no markdown fences."""


READABILITY_REVIEW_PROMPT = """You are a senior engineer specializing in code quality and maintainability.

{context}

Analyze the following {language} code for readability issues.
Focus on: naming clarity, function complexity, separation of concerns,
control flow clarity, abstraction quality, and cognitive load.

CODE:
```{language}
{code}
```

Return a JSON object with exactly this structure:
{{
  "agent_name": "Readability Review Agent",
  "domain": "Readability",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "Description of the readability problem",
      "suggestion": "Specific improvement",
      "line_number": <integer or null>,
      "code_snippet": "<snippet or null>",
      "confidence": <float 0.0-1.0>
    }}
  ],
  "overall_assessment": "One paragraph summary",
  "score": <integer 0-10>
}}

Return ONLY the JSON. No preamble, no markdown fences."""


BEST_PRACTICES_REVIEW_PROMPT = """You are a senior software architect.

{context}

Analyze the following {language} code for best practice violations.
Focus on: SOLID principles, error handling, input validation, anti-patterns,
testability, coupling, and language-specific conventions.

CODE:
```{language}
{code}
```

Return a JSON object with exactly this structure:
{{
  "agent_name": "Best Practices Agent",
  "domain": "Best Practices",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "Description of the violation",
      "suggestion": "Specific improvement",
      "line_number": <integer or null>,
      "code_snippet": "<snippet or null>",
      "confidence": <float 0.0-1.0>
    }}
  ],
  "overall_assessment": "One paragraph summary",
  "score": <integer 0-10>
}}

Return ONLY the JSON. No preamble, no markdown fences."""


AGGREGATION_PROMPT = """You are a principal engineer writing a technical review summary.

You have received structured reviews from 5 specialized AI reviewers.
The issue counts below are pre-computed — use them exactly as given.

REVIEWS:
{reviews_json}

ISSUE COUNTS:
- Critical: {critical_count}
- High: {high_count}
- Medium: {medium_count}
- Low: {low_count}

Return a JSON object with exactly this structure:
{{
  "overall_score": <float 0-10, weighted average of agent scores>,
  "critical_issues_count": {critical_count},
  "high_issues_count": {high_count},
  "medium_issues_count": {medium_count},
  "low_issues_count": {low_count},
  "top_priority_fixes": [
    "Most critical fix with specific action",
    "Second priority fix",
    "Third priority fix"
  ],
  "engineering_summary": "2-3 paragraph summary covering overall quality, most critical risks, and recommended action plan"
}}

Return ONLY the JSON. No preamble, no markdown fences."""