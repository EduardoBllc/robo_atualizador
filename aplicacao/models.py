from django.db import models

class Aplicacao(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    diretorio = models.CharField(max_length=128)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    comandos = models.ManyToManyField('Comando', blank=True, related_name='aplicacoes')
    remote = models.CharField(max_length=64, default='origin')
    branch_trunc = models.CharField(max_length=64, default='main')
    branch_dev = models.CharField(max_length=64, blank=True, null=True)
    branch_homolog = models.CharField(max_length=64, blank=True, null=True)
    branch_prod = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.nome}({self.diretorio})"

    class Meta:
        db_table = "aplicacao"
        verbose_name = "Aplicação"
        verbose_name_plural = "Aplicações"
        ordering = ["nome"]

class Comando(models.Model):
    comando = models.CharField(max_length=300)
    descricao = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.comando}"

    class Meta:
        db_table = "comando"
        verbose_name = "Comando"
        verbose_name_plural = "Comandos"
