from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests

class AgentStatusView(APIView):
    def get(self, request):
        dados: dict = {
            'status': 'ok',
        }
        return Response(dados, status=status.HTTP_200_OK)


class CentralStatusView(APIView):
    def get(self, request):
        dados: dict = {'status': 'ok', 'agents': []}

        from central.agent.models import Agent

        for cliente in Agent.objects.all():
            res_status_cliente = requests.get(f'{cliente.base_url}/status/', timeout=5)
            if res_status_cliente.status_code == 200:
                dados['agents'].append({
                    'id': cliente.id,
                    'ipaddr_host': cliente.netloc,
                    'descricao': cliente.name,
                    'status': res_status_cliente.json()
                })
            else:
                dados['agents'].append({
                    'id': cliente.id,
                    'ipaddr_host': cliente.netloc,
                    'descricao': cliente.name,
                    'status': f'erro ({res_status_cliente.status_code})'
                })


        return Response(dados, status=status.HTTP_200_OK)