from django.contrib import admin
from django.conf import settings
from clientes.models import Cliente

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ip', 'porta', 'data_cadastro', 'data_alteracao')
    search_fields = ('nome', 'ip')

if settings.IS_CENTRAL:
    admin.site.register(Cliente, ClienteAdmin)