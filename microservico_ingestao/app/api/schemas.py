from pydantic import BaseModel
from datetime import datetime

class ClienteResponse(BaseModel):
    id : int
    nome : str
    email: str | None
    telefone: str | None
    cpf_cnpj: str | None
    endereco_completo: str| None
    
    class Config:
        from_attributes = True # Permite retorna direto de SQLAlchemy

class ProdutoResponse(BaseModel):
    id : int
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