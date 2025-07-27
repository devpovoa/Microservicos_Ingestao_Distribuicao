import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Form, HTTPException
from pydantic import BaseModel
from app.core.database import Base, engine, SessionLocal
from app.workers.file_watcher import start_file_watcher
from typing import List
from sqlalchemy.orm import Session
from app.models.temp_models import ClienteTemp, ProdutoTemp, CompraTemp
from app.api.schemas import ClienteResponse, ProdutoResponse, CompraResponse
from app.core.security import verify_token, create_access_token
from app.core.config import settings


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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Endpoint para gerar o token JWT
@app.post("/token", response_model=TokenResponse, summary="Login e geração de token JWT")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == settings.admin_user and password == settings.admin_password:
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credencias inválidas")

@app.get("/status", summary="Status do microserviço (JWT protegido)")
async def status(user=Depends(verify_token)):
    return {"service": "ingestao", "status": "ok", "user": user["sub"]}
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/clientes", response_model=List[ClienteResponse], summary="Listar clientes normalizados")
def listar_clientes(user=Depends(verify_token), db: Session = Depends(get_db)):
    return db.query(ClienteTemp).all()

@app.get("/produtos", response_model=List[ProdutoResponse], summary="Listar produtos normalizados")
def listar_produtos(user=Depends(verify_token), db: Session = Depends(get_db)):
    return db.query(ProdutoTemp).all()

@app.get("/compras", response_model=List[CompraResponse], summary="Listar compras com clientes e produto")
def listar_compras(user=Depends(verify_token), db: Session = Depends(get_db)):
    compras = db.query(CompraTemp).all()
    return compras
