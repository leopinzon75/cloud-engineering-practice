from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Youtube", "status": "Pipeline de Ejercicio 1 funcionando perfectamente"}
