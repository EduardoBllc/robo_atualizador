from datetime import datetime

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from atualizacao.models import Atualizacao
from clientes.models import Cliente


class AtualizacaoView(APIView):
    def post(self, request):
        if settings.ATUALIZADOR_MESTRE:
            print('Eu sou o mestre')
            for cliente in Cliente.objects.all():
                url_atualizacao = f'{cliente.url_base}/atualizar/'

                try:
                    res = requests.post(url_atualizacao, timeout=10)
                    if res.status_code == 200:
                        print(f'Atualização enviada para {cliente.descricao} com sucesso.')
                    else:
                        print(f'Erro ao enviar atualização para {cliente.descricao}. Status code: {res.status_code}')
                except Exception as e:
                    print(f'Erro ao enviar atualização para {cliente.descricao}: {str(e)}')

        else:
            Atualizacao.objects.create(
                data=datetime.now(),
                versao_anterior='0.0.0',
                versao_atualizacao='1.0.0',
                status='S'
            )
            print('Eu sou o escravo')

        return Response(status=status.HTTP_200_OK)


