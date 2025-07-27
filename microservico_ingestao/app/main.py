from datetime import datetime
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Form, HTTPException
from pydantic import BaseModel
from app.core.database import Base, engine, SessionLocal
from app.workers.file_watcher import start_file_watcher
from typing import List
from sqlalchemy.orm import Session
from app.models.temp_models import ClienteTemp, ProdutoTemp, CompraTemp
from app.api.schemas import ClienteResponse, ProdutoResponse, CompraResponse, CompraCreate
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

@app.post("/compras", response_model=CompraCreate, summary="Criar uma venda via API")
def criar_compra(compra_data: CompraCreate, user=Depends(verify_token), db: Session = Depends(get_db)):
    
    data_hora = datetime.now()
    cliente = None
    if compra_data.cliente.cpf_cnpj:
        cliente = db.query(ClienteTemp).filter_by(cpf_cnpj=compra_data.cliente.cpf_cnpj).first()
    if not cliente:
        cliente = db.query(ClienteTemp).filter_by(nome=compra_data.cliente.nome).first()
    if not cliente:
        cliente = ClienteTemp(**compra_data.cliente.dict()) 
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    
    produto = db.query(ProdutoTemp).filter_by(nome_produto=compra_data.produto.nome_produto).first()
    if not produto:
        produto = ProdutoTemp(nome_produto=compra_data.produto.nome_produto)
        db.add(produto)
        db.commit()
        db.refresh(produto)
        
    valor_total = compra_data.quantidade * compra_data.valor_unitario
    compra = CompraTemp(
        cliente_id = cliente.id,
        produto_id = produto.id,
        quantidade = compra_data.quantidade,
        valor_unitario = compra_data.valor_unitario,
        valor_total = valor_total,
        data_hora = data_hora,
        forma_pagamento = compra_data.forma_pagamento
    )
    db.add(compra)
    db.commit()
    db.refresh(compra)
    
    return compra
