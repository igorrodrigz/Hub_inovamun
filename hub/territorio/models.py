from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q

# Create your models here.
class Municipio(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    codigo_ibge = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        validators=[RegexValidator(r'^\d{7}$', 'Informe o código IBGE com sete dígitos.')],
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Município"
        verbose_name_plural = "Municípios"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(latitude__isnull=True, longitude__isnull=True)
                    | (
                        Q(latitude__isnull=False, longitude__isnull=False)
                        & Q(latitude__gte=-90, latitude__lte=90)
                        & Q(longitude__gte=-180, longitude__lte=180)
                    )
                ),
                name='municipio_valid_coordinates',
            ),
        ]

    def clean(self):
        super().clean()
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError({
                'latitude': 'Informe latitude e longitude em conjunto.',
                'longitude': 'Informe latitude e longitude em conjunto.',
            })

    def __str__(self):
        return f"{self.nome} - ({self.uf})"