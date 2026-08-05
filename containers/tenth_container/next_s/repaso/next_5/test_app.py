import pytest
import os
import sys

def test_run_batch_success(monkeypatch):
    monkeypatch.setenv("SIMULAR_ERROR", "False")
    monkeypatch.setenv("TOTAL_ITEMS", "2")
    
    from app import run_batch
    try:
        run_batch()
    except SystemExit as e:
        pytest.fail(f"El script falló inesperadamente con código: {e}")

def test_run_batch_error_simulation(monkeypatch):
    monkeypatch.setenv("SIMULAR_ERROR", "True")
    monkeypatch.setenv("TOTAL_ITEMS", "5")
    
    from app import run_batch
    with pytest.raises(SystemExit) as exc_info:
        run_batch()
    
    assert exc_info.value.code == 1
