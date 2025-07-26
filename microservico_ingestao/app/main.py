from fastapi import FastAPI
from app.core.database import Base, engine
from app.models.temp_models import ClienteTemp, CompraTemp

# Cria as tabelas caso não existirem.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "Ingestão de Arquivos Excel",
    version = "1.0.0",
    description = "Microserviço 1 - FastAPI para ingestão de arquivos"
)

@app.get("/status")
async def status():
    return {"service": "ingestao", "status": "ok"}