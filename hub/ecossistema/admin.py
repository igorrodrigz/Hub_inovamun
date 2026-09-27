from django.contrib import admin

from .models import (
    Categoria,
    Problema,
    Solucao,
    Conexao,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
    )

    ordering = (
        "nome",
    )


@admin.register(Problema)
class ProblemaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "municipio",
        "categoria",
        "status",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "status",
        "categoria",
        "municipio__uf",
        "ativo",
    )

    search_fields = (
        "titulo",
        "descricao",
        "municipio__nome",
        "categoria__nome",
    )

    autocomplete_fields = (
        "municipio",
        "categoria",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "titulo",
    )


@admin.register(Solucao)
class SolucaoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "organizacao",
        "categoria",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "categoria",
        "ativo",
        "organizacao__tipo",
    )

    search_fields = (
        "titulo",
        "descricao",
        "organizacao__nome",
        "categoria__nome",
    )

    autocomplete_fields = (
        "organizacao",
        "categoria",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "titulo",
    )


@admin.register(Conexao)
class ConexaoAdmin(admin.ModelAdmin):
    list_display = (
        "problema",
        "solucao",
        "status",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "status",
        "ativo",
    )

    search_fields = (
        "problema__titulo",
        "solucao__titulo",
        "observacoes",
    )

    autocomplete_fields = (
        "problema",
        "solucao",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "-criado_em",
    )