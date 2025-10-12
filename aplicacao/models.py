from django.db import models
import git
from datetime import datetime

class Aplicacao(models.Model):
    nome = models.CharField(max_length=100)
    caminho = models.CharField(max_length=128)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    comandos = models.ManyToManyField('Comando', blank=True, related_name='aplicacoes')
    remote = models.CharField(max_length=64, default='origin')
    branch_trunc = models.CharField(max_length=64, default='main')
    branch_dev = models.CharField(max_length=64, blank=True, null=True)
    branch_homolog = models.CharField(max_length=64, blank=True, null=True)
    branch_prod = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.nome}({self.caminho})"

    class Meta:
        db_table = "aplicacao"
        verbose_name = "Aplicação"
        verbose_name_plural = "Aplicações"
        ordering = ["nome"]

    @property
    def repositorio(self):
        return git.Repo(self.caminho)

    @property
    def branch_ativa(self) -> git.Head | None:
        try:
            return self.repositorio.active_branch
        except TypeError:
            return None

    @property
    def commit_atual(self) -> git.Commit:
        return self.repositorio.head.commit

    @property
    def data_commit_atual(self) -> datetime:
        return self.commit_atual.committed_datetime

    @property
    def commit_atual_formatado(self) -> str:
        return f"{self.commit_atual.hexsha[:7]} - {self.data_commit_atual.strftime('%d/%m/%Y')}"

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

