import threading
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from app.api.schemas import (ClienteResponse, CompraCreate, CompraResponse,
                             ProdutoResponse)
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, verify_token
from app.models.temp_models import ClienteTemp, CompraTemp, ProdutoTemp
from app.tasks.publisher import publish_processed_data
from app.workers.file_watcher import start_file_watcher
from fastapi import Depends, FastAPI, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Cria as tabelas no primeiro start
Base.metadata.create_all(bind=engine)

watcher_thread = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global watcher_thread
    print("[INIT] Entrou no lifespan do FastAPI", flush=True)

    if watcher_thread is None or not watcher_thread.is_alive():
        watcher_thread = threading.Thread(
            target=start_file_watcher, daemon=True)
        watcher_thread.start()
        print("[WATCHER] iniciado em background!", flush=True)
    else:
        print("[WATCHER] já estava ativo, não duplicado.", flush=True)

    yield
    print("[SHUTDOWN] Encerrando recursos...", flush=True)


def create_app():
    return FastAPI(
        title="Serviço de Ingestão de Dados",
        version="1.0.0",
        description=(
            "Este microserviço é responsável por ingerir e validar dados enviados via arquivos Excel (.xlsx) "
            "ou requisições JSON. Após a validação, os dados são enviados de forma assíncrona para uma fila "
            "RabbitMQ, onde são processados por workers Celery para persistência e tratamento. "
            "Ideal para ingestão massiva e desacoplada de dados em tempo real."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )


app = create_app()

# Models auxiliares


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Dependência de sessão DB

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint


@app.post("/token", response_model=TokenResponse, summary="Login e geração de token JWT")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == settings.admin_user and password == settings.admin_password:
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credencias inválidas")


@app.get("/status", summary="Status do microserviço (JWT protegido)")
async def status(user=Depends(verify_token)):
    return {"service": "ingestao", "status": "ok", "user": user["sub"]}


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

    data_hora = datetime.now(ZoneInfo("America/Sao_Paulo"))

    cliente = None
    if compra_data.cliente.cpf_cnpj:
        cliente = db.query(ClienteTemp).filter_by(
            cpf_cnpj=compra_data.cliente.cpf_cnpj).first()
    if not cliente:
        cliente = db.query(ClienteTemp).filter_by(
            nome=compra_data.cliente.nome).first()
    if not cliente:
        cliente = ClienteTemp(**compra_data.cliente.dict())
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    produto = db.query(ProdutoTemp).filter_by(
        nome_produto=compra_data.produto.nome_produto).first()
    if not produto:
        produto = ProdutoTemp(nome_produto=compra_data.produto.nome_produto)
        db.add(produto)
        db.commit()
        db.refresh(produto)

    # Cria compra TEMP
    valor_total = compra_data.quantidade * compra_data.valor_unitario
    compra = CompraTemp(
        cliente_id=cliente.id,
        produto_id=produto.id,
        quantidade=compra_data.quantidade,
        valor_unitario=compra_data.valor_unitario,
        valor_total=valor_total,
        data_hora=data_hora,
        forma_pagamento=compra_data.forma_pagamento
    )
    db.add(compra)
    db.commit()
    db.refresh(compra)

    payload = {
        "id": compra.id,
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "cpf_cnpj": cliente.cpf_cnpj,
            "endereco_completo": cliente.endereco_completo,
        },
        "produto": {
            "id": produto.id,
            "nome_produto": produto.nome_produto,
        },
        "quantidade": int(compra.quantidade),
        "valor_unitario": float(compra.valor_unitario),
        "valor_total": float(compra.valor_total),
        "data_hora": compra.data_hora.isoformat(),
        "forma_pagamento": compra.forma_pagamento,
    }

    task_id = publish_processed_data(payload)
    print(
        f"[API] Publicado no RabbitMQ (processed_data). task_id={task_id}", flush=True)

    return compra
