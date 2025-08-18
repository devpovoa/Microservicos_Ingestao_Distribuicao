from __future__ import annotations

from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=200, unique=True)
    preco_atual = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["nome"])
        ]

    def __str__(self):
        return self.nome
