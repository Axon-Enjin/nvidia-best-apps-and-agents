"""Shared synthetic evidence has one authoritative copy at tests/fixtures."""
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
