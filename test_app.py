import pytest
from app import run_batch

def test_run_batch_exito(monkeypatch):
    monkeypatch.setenv("SIMULAR_ERROR", "False")
    monkeypatch.setenv("TOTAL_ITEMS", "5")
    processed = run_batch()
    assert processed == 5

def test_run_batch_falla_controlada(monkeypatch):
    monkeypatch.setenv("SIMULAR_ERROR", "True")
    monkeypatch.setenv("TOTAL_ITEMS", "5")
    with pytest.raises(RuntimeError):
        run_batch()
