from django.contrib import admin
from django.conf import settings
from repositorio.models import Repositorio

class RepositorioAdmin(admin.ModelAdmin):
    model = Repositorio
    list_display = ('nome', 'caminho', 'branch_ativa', 'data_commit_atual', 'data_cadastro', 'data_alteracao')
    readonly_fields = ('branch_ativa', 'commit_atual_formatado', )
    search_fields = ('nome',)

if not settings.SERVIDOR_CENTRAL:
    admin.site.register(Repositorio, RepositorioAdmin)