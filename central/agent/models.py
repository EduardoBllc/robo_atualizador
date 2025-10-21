from django.db import models

# Modelo que representa um servidor cliente, que ficar "escutando" esperando por atualizações do projeto para atualizar
class Agent(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    uses_tls = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    auto_update = models.BooleanField(default=True)

    class Meta:
        db_table = 'agent'
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        unique_together = ('ip_address', 'port')
        ordering = ['id']

    @property
    def schema_http(self):
        return 'https' if self.uses_tls else 'http'

    @property
    def base_url(self):
        return f'{self.schema_http}://{self.netloc}'

    @property
    def netloc(self):
        return f'{self.ip_address}:{self.port}'

    def __str__(self):
        return f'{self.name} ({self.netloc})'