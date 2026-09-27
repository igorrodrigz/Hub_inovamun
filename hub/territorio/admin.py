from django.contrib import admin
from django.contrib import messages

from .models import Municipio
from .services import IBGECoordinateError, get_municipality_reference_coordinates
# Register your models here.

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo_ibge', 'uf', 'latitude', 'longitude', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('uf', 'ativo')
    search_fields = ('nome', 'codigo_ibge', 'estado', 'uf')
    readonly_fields = ('criado_em', 'atualizado_em')
    ordering = ('nome',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['codigo_ibge'].required = True
        form.base_fields['codigo_ibge'].help_text = 'Código oficial do município no IBGE, com sete dígitos.'
        form.base_fields['latitude'].help_text = 'Geradas pelo IBGE se ambas as coordenadas forem deixadas vazias.'
        form.base_fields['longitude'].help_text = 'Coordenadas preenchidas manualmente serão preservadas.'
        return form

    def save_model(self, request, obj, form, change):
        coordinates_missing = obj.latitude is None and obj.longitude is None
        super().save_model(request, obj, form, change)

        if not coordinates_missing or not obj.codigo_ibge:
            return

        try:
            obj.latitude, obj.longitude = get_municipality_reference_coordinates(obj.codigo_ibge)
        except IBGECoordinateError:
            self.message_user(
                request,
                'Município salvo, mas não foi possível obter as coordenadas no IBGE. Salve novamente para tentar de novo.',
                level=messages.WARNING,
            )
            return

        obj.save(update_fields=('latitude', 'longitude', 'atualizado_em'))
        self.message_user(
            request,
            'Coordenadas de referência preenchidas a partir da malha municipal do IBGE.',
            level=messages.SUCCESS,
        )