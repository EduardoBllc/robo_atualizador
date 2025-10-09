from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests

from clientes.models import Cliente
from clientes.serializer import ClienteSerializer
from clientes.services import envia_cadastro_cliente_central, cadastra_cliente


class ClientesView(APIView):

    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClienteSerializer(data=request.data)

        if serializer.is_valid():
            if settings.SERVIDOR_CENTRAL:
                status_res, resposta = cadastra_cliente(serializer)
            else:
                status_res, resposta = envia_cadastro_cliente_central(serializer)
        else:
            status_res = status.HTTP_400_BAD_REQUEST
            resposta = {'error': 'Dados inválidos.', 'details': serializer.errors}

        return Response(resposta, status=status_res)
