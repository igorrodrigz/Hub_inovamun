from django.db import models

# Create your models here.

class Organizacao(models.Model):
    class Tipo(models.TextChoices):
        EMPRESA = 'EMPRESA', 'Empresa'
        STARTUP = 'STARTUP', 'Startup'
        INVESTIDOR = 'INVESTIDOR', 'Investidor'

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cnpj = models.CharField(max_length=14)
    ativo = models.BooleanField(default=True)
    descricao = models.TextField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    municipio = models.ForeignKey('territorio.Municipio', on_delete=models.SET_NULL, blank=True, null=True, related_name='organizacoes')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self):
        return f"{self.nome}"