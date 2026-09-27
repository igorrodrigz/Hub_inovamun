from django.db import models

# Create your models here.

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return f"{self.nome}"

class Problema(models.Model):

    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        RESOLVIDO = 'RESOLVIDO', 'Resolvido'

    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    municipio = models.ForeignKey('territorio.Municipio', on_delete=models.SET_NULL, blank=True, null=True, related_name='problemas')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTO)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = "Problema"
        verbose_name_plural = "Problemas"

    def __str__(self):
        return f"{self.titulo}"

class Solucao(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    organizacao = models.ForeignKey('organizacoes.Organizacao', on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = "Solução"
        verbose_name_plural = "Soluções"

    def __str__(self):
        return f"{self.titulo}"

class Conexao(models.Model):
    problema = models.ForeignKey(Problema, on_delete=models.CASCADE)
    solucao = models.ForeignKey(Solucao, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Problema.Status.choices, default=Problema.Status.ABERTO)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['problema']
        verbose_name = "Conexão"
        verbose_name_plural = "Conexões"

    def __str__(self):
        return f"{self.problema} -> {self.solucao}"