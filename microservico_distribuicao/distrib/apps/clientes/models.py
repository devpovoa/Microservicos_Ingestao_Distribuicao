from __future__ import annotations

from django.core.validators import RegexValidator
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\d+$",
                message="Informe apenas dígitos.",
            )
        ],
        help_text="Apenas dígitos",
    )
    cpf_cnpj = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{11,14}$",
                message="CPF/CNPJ deve conter de 11 a 14 dígitos.",
            )
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["nome"]),
        ]
        constraints = [
            # Evita duplicidade quando não houver documento.
            models.UniqueConstraint(
                fields=["nome", "email"],
                name="uniq_cliente_nome_email_when_no_doc",
                condition=models.Q(cpf_cnpj__isnull=True),
            ),
        ]

    def __str__(self):
        base = self.nome
        if self.cpf_cnpj:
            base += f"({self.cpf_cnpj})"
        return base


class Endereco(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="enderecos")
    endereco_completo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "endereco_completo"],
                name="uniq_endereco_por_cliente",
            )
        ]

    def __str__(self):
        return f"{self.cliente.nome} - {self.endereco_completo[:60]}..."
