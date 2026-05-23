import pytest
from unittest.mock import patch, MagicMock
from backend.core.analyzer import (
    _extract_imports,
    _count_functions,
    _estimate_complexity,
    analyze_code,
)


SAMPLE_PYTHON = """
import sqlite3
import hashlib
from os import path

password = "admin123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchone()

def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
"""

SIMPLE_CODE = """
def hello():
    print("hello world")
"""


class TestExtractImports:
    def test_detects_standard_imports(self):
        imports = _extract_imports(SAMPLE_PYTHON)
        assert "sqlite3" in imports
        assert "hashlib" in imports

    def test_detects_from_imports(self):
        imports = _extract_imports(SAMPLE_PYTHON)
        assert "os" in imports

    def test_empty_code(self):
        imports = _extract_imports("")
        assert imports == []

    def test_no_imports(self):
        imports = _extract_imports("x = 1\ny = 2")
        assert imports == []

    def test_deduplicates_imports(self):
        code = "import os\nimport os\nimport os"
        imports = _extract_imports(code)
        assert imports.count("os") == 1

    def test_handles_syntax_error_gracefully(self):
        bad_code = "import sqlite3\ndef broken(\nno closing"
        imports = _extract_imports(bad_code)
        assert "sqlite3" in imports


class TestCountFunctions:
    def test_counts_functions(self):
        assert _count_functions(SAMPLE_PYTHON) == 2

    def test_zero_functions(self):
        assert _count_functions("x = 1") == 0

    def test_simple_function(self):
        assert _count_functions(SIMPLE_CODE) == 1

    def test_handles_syntax_error(self):
        result = _count_functions("def broken(\nno close")
        assert isinstance(result, int)


class TestEstimateComplexity:
    def test_low_complexity(self):
        assert _estimate_complexity(10, 1) == "low"

    def test_medium_complexity(self):
        assert _estimate_complexity(50, 3) == "medium"

    def test_high_complexity(self):
        assert _estimate_complexity(150, 10) == "high"

    def test_very_high_complexity(self):
        assert _estimate_complexity(400, 20) == "very_high"

    def test_boundary_low_medium(self):
        assert _estimate_complexity(29, 1) == "low"
        assert _estimate_complexity(30, 1) == "medium"


class TestAnalyzeCode:
    @patch("backend.core.analyzer._get_risk_flags")
    def test_detects_database_access(self, mock_flags):
        mock_flags.return_value = []
        meta = analyze_code(SAMPLE_PYTHON, "python")
        assert meta.has_database_access is True

    @patch("backend.core.analyzer._get_risk_flags")
    def test_detects_crypto(self, mock_flags):
        mock_flags.return_value = []
        meta = analyze_code(SAMPLE_PYTHON, "python")
        assert meta.has_crypto is True

    @patch("backend.core.analyzer._get_risk_flags")
    def test_no_network_in_sample(self, mock_flags):
        mock_flags.return_value = []
        meta = analyze_code(SAMPLE_PYTHON, "python")
        assert meta.has_network_calls is False

    @patch("backend.core.analyzer._get_risk_flags")
    def test_returns_code_metadata(self, mock_flags):
        mock_flags.return_value = ["hardcoded credential"]
        meta = analyze_code(SAMPLE_PYTHON, "python")
        assert meta.language == "python"
        assert meta.line_count > 0
        assert meta.function_count == 2
        assert meta.risk_flags == ["hardcoded credential"]

    @patch("backend.core.analyzer._get_risk_flags")
    def test_simple_clean_code(self, mock_flags):
        mock_flags.return_value = []
        meta = analyze_code(SIMPLE_CODE, "python")
        assert meta.has_database_access is False
        assert meta.has_crypto is False
        assert meta.has_network_calls is False
        assert meta.function_count == 1