from django.db import models

# Modelo que representa um servidor cliente, que ficar "escutando" esperando por atualizações do projeto para atualizar
class Cliente(models.Model):
    descricao = models.TextField(max_length=500)
    ip = models.GenericIPAddressField()
    porta = models.IntegerField()
    usa_tls = models.BooleanField(default=False)

    class Meta:
        db_table = 'clientes'
        unique_together = ('ip', 'porta')
        ordering = ['id']

    @property
    def url_base(self):
        protocolo = 'https:' if self.usa_tls else 'http:'
        return f'{protocolo}//{self.ip}:{self.porta}'