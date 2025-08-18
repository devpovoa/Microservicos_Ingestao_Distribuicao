from __future__ import annotations

from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .choices import FORMA_PAGAMENTO_CHOICES, OUTROS


class Compra(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="compras")
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name="compras")
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)

    forma_pagamento = models.CharField(
        max_length=20, choices=FORMA_PAGAMENTO_CHOICES, default=OUTROS)
    data_hora = models.DateTimeField(default=timezone.now)

    # Idempotência: hash único da compra
    id_mensagem = models.CharField(max_length=64, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["data_hora"]),
            models.Index(fields=["produto", "data_hora"]),
            models.Index(fields=["cliente", "data_hora"]),
        ]

    def __str__(self):
        return f"{self.cliente} - {self.produto} - {self.valor_total} em {self.data_hora:%Y-%m-%d %H:%M}"
