import pytest
from app import run_service

def test_run_service_exito(monkeypatch):
    monkeypatch.setenv("FAIL_FAST", "False")
    monkeypatch.setenv("MAX_RETRIES", "3")
    assert run_service() is True

def test_run_service_falla_controlada(monkeypatch):
    monkeypatch.setenv("FAIL_FAST", "True")
    monkeypatch.setenv("MAX_RETRIES", "3")
    with pytest.raises(ConnectionError):
        run_service()
