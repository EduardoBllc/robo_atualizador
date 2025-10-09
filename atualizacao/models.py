from django.db import models

# Opções de status (S = Sucesso, E = ERRO)
class StatusAtualizacao(models.TextChoices):
    sucesso = 'S'
    erro = 'E'

class Atualizacao(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    versao_anterior = models.CharField(max_length=32)
    versao_atualizacao = models.CharField(max_length=32)
    status = models.CharField(max_length=1, choices=StatusAtualizacao)

    class Meta:
        db_table = 'atualizacoes'
        verbose_name = 'Atualização'
        verbose_name_plural = 'Atualizações'
        ordering = ['-data']
