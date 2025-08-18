from django.contrib import admin

from .models import Cliente, Endereco


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "cpf_cnpj", "telefone", "created_at")
    search_fields = ("nome", "email", "cpf_cnpj")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "endereco_completo", "created_at")
    search_fields = ("cliente__name", "endereco_completo")
    list_filter = ("created_at",)
