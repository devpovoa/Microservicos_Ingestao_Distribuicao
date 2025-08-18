from django.contrib import admin

from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco_atual", "ativo", "created_at")
    search_fields = ("nome",)
    list_filter = ("ativo", "created_at")
    ordering = ("nome",)
