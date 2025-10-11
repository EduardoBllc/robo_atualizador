from django.db import models

# Modelo que representa um servidor cliente, que ficar "escutando" esperando por atualizações do projeto para atualizar
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    porta = models.IntegerField()
    usa_tls = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('ip', 'porta')
        ordering = ['id']

    @property
    def url_base(self):
        protocolo = 'https:' if self.usa_tls else 'http:'
        return f'{protocolo}//{self.ipaddr_host}'

    @property
    def ipaddr_host(self):
        return f'{self.ip}:{self.porta}'

    def __str__(self):
        return f'{self.nome} ({self.ip}:{self.porta})'