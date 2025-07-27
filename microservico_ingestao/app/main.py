import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import Base, engine
from app.workers.file_watcher import start_file_watcher

# Cria as tabelas no primeiro start
Base.metadata.create_all(bind=engine)

watcher_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global watcher_thread
    print("[INIT] Entrou no lifespan do FastAPI", flush=True)

    if watcher_thread is None or not watcher_thread.is_alive():
        watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
        watcher_thread.start()
        print("[WATCHER] iniciado em background!", flush=True)
    else:
        print("[WATCHER] já estava ativo, não duplicado.", flush=True)
    
    yield
    print("[SHUTDOWN] Encerrando recursos...", flush=True)

app = FastAPI(
    title="Ingestão de Arquivos Excel",
    version="1.0.0",
    description="Microserviço 1 - FastAPI para ingestão de arquivos",
    lifespan=lifespan
)

@app.get("/status")
async def status():
    return {"service": "ingestao", "status": "ok"}
