import json
import ast
from typing import List, Optional
from backend.schemas.review_schemas import CodeMetadata
from backend.core.llm import get_llm

DATABASE_IMPORTS = {"sqlite3", "psycopg2", "pymysql", "sqlalchemy", "pymongo", "redis"}
NETWORK_IMPORTS  = {"requests", "httpx", "aiohttp", "urllib", "socket", "boto3"}
CRYPTO_IMPORTS   = {"hashlib", "cryptography", "jwt", "bcrypt", "hmac", "ssl"}
AUTH_IMPORTS     = {"jwt", "oauth", "authlib", "flask_login", "django.contrib.auth"}
FILEIO_IMPORTS   = {"pathlib", "shutil", "os.path", "open"}

AUTH_KEYWORDS    = {"password", "token", "secret", "api_key", "auth", "login", "session"}
INPUT_KEYWORDS   = {"input(", "request.args", "request.form", "request.json",
                    "request.data", "sys.argv", "os.environ"}


def _extract_imports(code: str) -> List[str]:
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
    except SyntaxError:
        for line in code.splitlines():
            line = line.strip()
            if line.startswith("import "):
                imports.append(line.split()[1].split(".")[0])
            elif line.startswith("from "):
                parts = line.split()
                if len(parts) > 1:
                    imports.append(parts[1].split(".")[0])
    return list(set(imports))


def _count_functions(code: str) -> int:
    try:
        tree = ast.parse(code)
        return sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    except SyntaxError:
        return code.count("def ") + code.count("function ")


def _estimate_complexity(line_count: int, function_count: int) -> str:
    if line_count < 30:
        return "low"
    elif line_count < 100:
        return "medium"
    elif line_count < 300:
        return "high"
    return "very_high"


def _get_risk_flags(code: str, imports: List[str], metadata: dict) -> List[str]:
    prompt = f"""Analyze this code and return a JSON array of specific risk flags detected.
Risk flags should be short phrases describing concrete risks, not general categories.
Examples: "string-concatenated SQL query", "MD5 used for password hashing",
"hardcoded credential", "unbounded loop over user input", "no input validation on user data".

Only include flags for risks you can clearly see in the code.
Return ONLY a JSON array of strings, nothing else.

CODE:
{code}

CONTEXT:
- Imports detected: {imports}
- Has database access: {metadata['has_database_access']}
- Has user input: {metadata['has_user_input']}
- Has crypto: {metadata['has_crypto']}
"""
    try:
        llm = get_llm(temperature=0.0)
        response = llm.invoke(prompt)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return []


def analyze_code(code: str, language: str) -> CodeMetadata:
    imports = _extract_imports(code)
    import_set = set(i.lower() for i in imports)
    code_lower = code.lower()

    has_database = bool(import_set & DATABASE_IMPORTS)
    has_network  = bool(import_set & NETWORK_IMPORTS)
    has_crypto   = bool(import_set & CRYPTO_IMPORTS)
    has_auth     = bool(import_set & AUTH_IMPORTS) or any(k in code_lower for k in AUTH_KEYWORDS)
    has_file_io  = bool(import_set & FILEIO_IMPORTS) or "open(" in code
    has_user_input = any(k in code for k in INPUT_KEYWORDS)

    line_count     = len([l for l in code.splitlines() if l.strip()])
    function_count = _count_functions(code)
    complexity     = _estimate_complexity(line_count, function_count)

    meta_dict = {
        "has_database_access": has_database,
        "has_network_calls":   has_network,
        "has_auth_logic":      has_auth,
        "has_user_input":      has_user_input,
        "has_crypto":          has_crypto,
        "has_file_io":         has_file_io,
    }

    risk_flags = _get_risk_flags(code, imports, meta_dict)

    return CodeMetadata(
        language=language,
        line_count=line_count,
        function_count=function_count,
        imports=imports,
        complexity_estimate=complexity,
        risk_flags=risk_flags,
        **meta_dict,
    )