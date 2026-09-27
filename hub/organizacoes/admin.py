from django.contrib import admin
from .models import Organizacao
# Register your models here.
@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'cnpj', 'ativo', 'municipio', 'criado_em', 'atualizado_em')
    list_filter = ('tipo', 'ativo', 'municipio')
    search_fields = ('municipio__nome', 'cnpj', 'email','municipio__uf')
