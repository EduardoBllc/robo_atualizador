from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests
from django.conf import settings

from clientes.models import Cliente


class StatusView(APIView):
    def get(self, request):
        dados: dict = {
            'status': 'ok',
        }

        if settings.SERVIDOR_CENTRAL:
            dados['clientes'] = []

            for cliente in Cliente.objects.all():
                res_status_cliente = requests.get(f'{cliente.url_base}/status/', timeout=5)
                if res_status_cliente.status_code == 200:
                    dados['clientes'].append({
                        'id': cliente.id,
                        'ipaddr_host': cliente.ipaddr_host,
                        'descricao': cliente.nome,
                        'status': res_status_cliente.json()
                    })
                else:
                    dados['clientes'].append({
                        'id': cliente.id,
                        'ipaddr_host': cliente.ipaddr_host,
                        'descricao': cliente.nome,
                        'status': f'erro ({res_status_cliente.status_code})'
                    })

        return Response(dados, status=status.HTTP_200_OK)
