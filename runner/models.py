from django.db import models

# Opções de status (S = Sucesso, E = ERRO)
class UpdateStatus(models.TextChoices):
    sucesso = 'S'
    erro = 'E'

class UpdateLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    before_version = models.CharField(max_length=32)
    updated_version = models.CharField(max_length=32)
    branch = models.CharField(max_length=128, blank=True, null=True)
    commit_hash = models.CharField(max_length=40, blank=True, null=True)
    status = models.CharField(max_length=1, choices=UpdateStatus)

    class Meta:
        db_table = 'update_log'
        verbose_name = 'Update Log'
        verbose_name_plural = 'Update Logs'
        ordering = ['-timestamp']
