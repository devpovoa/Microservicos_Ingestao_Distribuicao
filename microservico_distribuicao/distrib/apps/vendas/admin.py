from django.contrib import admin

from .models import Compra


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("cliente", "produto", "quantidade", "preco_unitario",
                    "valor_total", "forma_pagamento", "data_hora", "id_mensagem")
    search_fields = ("cliente__nome", "cliente__cpf_cnpj",
                     "produto__nome", "id_mensagem")
    list_filter = ("forma_pagamento", "data_hora", "created_at")
    date_hierarchy = "data_hora"
    ordering = ("-data_hora",)
