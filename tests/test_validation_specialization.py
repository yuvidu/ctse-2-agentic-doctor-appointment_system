"""Specialization validation accepts LLM casing (e.g. cardiology vs Cardiology)."""

from __future__ import annotations

import tools.intent_tools.validation_tool as vt


def test_validate_input_case_insensitive_canonicalizes(monkeypatch) -> None:
    monkeypatch.setattr(vt, "_cached", ["Cardiology", "Dermatology"])
    data = {"specialization": "cardiology", "date": "2026-05-02", "time_preference": "morning"}
    out = vt.validate_input(data)
    assert out["is_valid"] is True
    assert out["errors"] == []
    assert data["specialization"] == "Cardiology"


def test_validate_input_unknown_specialty_still_errors(monkeypatch) -> None:
    monkeypatch.setattr(vt, "_cached", ["Cardiology"])
    data = {"specialization": "Alienology"}
    out = vt.validate_input(data)
    assert out["is_valid"] is False
    assert "Invalid specialization" in out["errors"]


def test_validate_input_cardiologist_job_title(monkeypatch) -> None:
    """LLM often returns 'Cardiologist' for 'I need a cardiologist…'."""
    monkeypatch.setattr(vt, "_cached", ["Cardiology", "Dermatology"])
    data = {"specialization": "Cardiologist"}
    out = vt.validate_input(data)
    assert out["is_valid"] is True
    assert data["specialization"] == "Cardiology"
