from datetime import datetime

from pydantic import BaseModel


# Saída da API
class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str | None = None
    telefone: str | None = None
    cpf_cnpj: str | None = None
    endereco_completo: str | None = None

    class Config:
        from_attributes = True  # Permite converter diretamente de modelos
        # SQLAlchemy


class ProdutoResponse(BaseModel):
    id: int
    nome_produto: str

    class Config:
        from_attributes = True


class CompraResponse(BaseModel):
    id: int
    cliente: ClienteResponse
    produto: ProdutoResponse
    quantidade: int
    valor_unitario: float
    valor_total: float
    data_hora: datetime
    forma_pagamento: str

    class Config:
        from_attributes = True

# Entradas da API


class ClienteCreate(BaseModel):
    nome: str
    email: str | None = None
    telefone: str | None = None
    cpf_cnpj: str | None = None
    endereco_completo: str | None = None


class ProdutoCreate(BaseModel):
    nome_produto: str


class CompraCreate(BaseModel):
    cliente: ClienteCreate
    produto: ProdutoCreate
    quantidade: int
    valor_unitario: float
    forma_pagamento: str
