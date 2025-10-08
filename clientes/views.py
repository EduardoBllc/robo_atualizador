from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests

from clientes.models import Cliente
from clientes.serializer import ClienteSerializer


# Create your views here.
class ClientesView(APIView):

    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClienteSerializer(data=request.data)

        if serializer.is_valid():
            dados_serializados = serializer.validated_data

            # Realizar requisição de status para garantir que o cliente está acessível
            protocolo = 'https:' if dados_serializados['usa_tls'] else 'http:'
            url = f'{protocolo}//{dados_serializados["ip"]}:{dados_serializados["porta"]}/status/'

            try:
                res = requests.get(url, timeout=5)
                if res.status_code != 200:
                    raise Exception('Status code diferente de 200')
                status_ok = res.json().get('ok', False)
            except Exception as e:
                status_ok = False

            if status_ok:
                instance = serializer.save()
                status_res = status.HTTP_201_CREATED
                resposta = {'message': 'Cliente cadastrado com sucesso.', 'cliente_id': instance.id}
            else:
                status_res = status.HTTP_400_BAD_REQUEST
                resposta = {'error': 'Não foi possível acessar clietne.'}
        else:
            status_res = status.HTTP_400_BAD_REQUEST
            resposta = {'error': 'Dados inválidos.', 'details': serializer.errors }

        return Response(resposta, status=status_res)
