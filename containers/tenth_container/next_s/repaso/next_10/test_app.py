import pytest
from app import acquire_dynamo_lock, release_dynamo_lock, init_infrastructure

def test_infrastructure_and_locking():
    # 1. Probar inicialización de infraestructura
    init_infrastructure()
    
    # 2. Adquirir candado exitosamente
    assert acquire_dynamo_lock("pytest_lock") == True
    
    # 3. Intentar adquirir el mismo candado (debe bloquearse/retornar False)
    assert acquire_dynamo_lock("pytest_lock") == False
    
    # 4. Liberar el candado
    release_dynamo_lock("pytest_lock")
    
    # 5. Adquirir nuevamente tras liberación (debe funcionar)
    assert acquire_dynamo_lock("pytest_lock") == True
    release_dynamo_lock("pytest_lock")
