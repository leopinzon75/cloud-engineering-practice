import pytest
import os
import subprocess

def test_run_batch_success():
    """Prueba que el proceso termine exitosamente cuando SIMULAR_ERROR es False."""
    env = os.environ.copy()
    env["SIMULAR_ERROR"] = "False"
    env["TOTAL_ITEMS"] = "2"
    
    result = subprocess.run(["python", "app.py"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "TRABAJO COMPLETADO CON ÉXITO" in result.stdout

def test_run_batch_simulated_failure():
    """Prueba que el proceso falle (exit code 1) cuando SIMULAR_ERROR es True."""
    env = os.environ.copy()
    env["SIMULAR_ERROR"] = "True"
    env["TOTAL_ITEMS"] = "5"
    
    result = subprocess.run(["python", "app.py"], capture_output=True, text=True, env=env)
    assert result.returncode == 1
    assert "El contenedor experimentó una falla crítica" in result.stdout
