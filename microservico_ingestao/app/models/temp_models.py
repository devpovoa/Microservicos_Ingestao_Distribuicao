from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClienteTemp(Base):
    __tablename__ = "clientes_temp"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    telefone = Column(String(50), nullable=True)
    cpf_cnpj = Column(String(20), unique=True, index=True, nullable=True)
    endereco_completo = Column(String(255), nullable=True)

    compras = relationship(
        "CompraTemp", back_populates="cliente", cascade="all, delete-orphan", passive_deletes=True)


class ProdutoTemp(Base):
    __tablename__ = "produtos_temp"

    id = Column(Integer, primary_key=True, index=True)
    nome_produto = Column(String(255), unique=True, index=True, nullable=False)

    compras = relationship(
        "CompraTemp", back_populates="produto", cascade="all, delete-orphan", passive_deletes=True)


class CompraTemp(Base):
    __tablename__ = "compras_temp"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey(
        "clientes_temp.id", ondelete="CASCADE"), nullable=False)
    produto_id = Column(Integer, ForeignKey(
        "produtos_temp.id", ondelete="CASCADE"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    forma_pagamento = Column(String(50), nullable=False)

    cliente = relationship("ClienteTemp", back_populates="compras")
    produto = relationship("ProdutoTemp", back_populates="compras")
