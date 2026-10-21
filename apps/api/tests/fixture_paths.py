"""Shared synthetic evidence has one authoritative copy at the repository root."""
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
