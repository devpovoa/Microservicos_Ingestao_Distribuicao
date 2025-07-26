from fastapi import FastAPI

app = FastAPI(
    title = "Ingestão de Arquivos Excel",
    version = "1.0.0",
    description = "Microserviço 1 - FastAPI para ingestão de arquivos"
)

@app.get("/status")
async def status():
    return {"service": "ingestao", "status": "ok"}