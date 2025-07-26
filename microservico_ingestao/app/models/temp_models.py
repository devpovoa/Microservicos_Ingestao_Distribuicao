from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ClienteTemp(Base):
    __tablename__ = "clientes_temp"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    compras = relationship("CompraTemp", back_populates="cliente", cascade="all, delete-orphan")

class CompraTemp(Base):
    __tablename__ = "compras_temp"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes_temp.id", ondelete="CASCADE"), nullable=False)
    produto = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    cliente = relationship("ClienteTemp", back_populates="compras")
    