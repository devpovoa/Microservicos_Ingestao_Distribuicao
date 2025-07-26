import threading
from contextlib import asynccontextmanager
from app.workers.file_watcher import start_file_watcher
from fastapi import FastAPI
from app.core.database import Base, engine
from app.models.temp_models import ClienteTemp, CompraTemp

# Cria as tabelas caso não existirem.
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o Watchdog em thread paralelo
    print("Entrou no lifespan do FastAPI", flush=True)
    
    watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
    watcher_thread.start()
    
    print("Watchdog iniciado em background!", flush=True)
    
    # o app vai rodar enquanto a thread segue ativa
    yield 
    
    # SHUTDOWN caso no future precisar
    # await connection.close()
    print("Encerrando recursos...", flush=True)

app = FastAPI(
    title = "Ingestão de Arquivos Excel",
    version = "1.0.0",
    description = "Microserviço 1 - FastAPI para ingestão de arquivos",
    lifespan=lifespan
)

@app.get("/status")
async def status():
    return {"service": "ingestao", "status": "ok"}