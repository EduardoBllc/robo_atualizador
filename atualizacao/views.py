import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from repositorio.models import Repositorio
from clientes.models import Cliente
from atualizacao.services import update


class AtualizacaoView(APIView):
    def post(self, request):
        """
        Endpoint para iniciar o processo de atualização.

        Params:
        - branch: nome do branch que recebeu atualização. Só serà enviada atualização para as aplicações que estão com
        essa branch ativa.
        """

        branch: str = request.data.get('branch')

        if settings.IS_CENTRAL:
            for cliente in Cliente.objects.all():
                url_atualizacao = f'{cliente.url_base}/atualizar/'
                body = {
                    'branch': branch
                }
                try:
                    res = requests.post(url_atualizacao, timeout=10, data=body)
                    if res.status_code == 200:
                        print(f'Atualização enviada para {cliente.nome} com sucesso.')
                    else:
                        print(f'Erro ao enviar atualização para {cliente.nome}. Status code: {res.status_code}')
                except Exception as e:
                    print(f'Erro ao enviar atualização para {cliente.nome}: {str(e)}')

        else:
            for repo in Repositorio.objects.all():
                if repo.branch_ativa.name == branch:
                    update(repo)


        return Response(status=status.HTTP_200_OK)


