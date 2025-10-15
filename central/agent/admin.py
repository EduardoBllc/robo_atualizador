from django.contrib import admin
from django.conf import settings
from central.agent.models import Agent

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ip_address', 'port', 'data_cadastro', 'data_alteracao')
    search_fields = ('nome', 'ip_address')

if settings.IS_CENTRAL:
    admin.site.register(Agent, ClienteAdmin)