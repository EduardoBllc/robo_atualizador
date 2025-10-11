from django.db import models

# Opções de status (S = Sucesso, E = ERRO)
class StatusAtualizacao(models.TextChoices):
    sucesso = 'S'
    erro = 'E'

class LogAtualizacao(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    versao_anterior = models.CharField(max_length=32)
    versao_atualizacao = models.CharField(max_length=32)
    branch = models.CharField(max_length=128, blank=True, null=True)
    hash_commit = models.CharField(max_length=40, blank=True, null=True)
    status = models.CharField(max_length=1, choices=StatusAtualizacao)

    class Meta:
        db_table = 'log_atualizacao'
        verbose_name = 'Log de Atualização'
        verbose_name_plural = 'Logs de Atualização'
        ordering = ['-data']
