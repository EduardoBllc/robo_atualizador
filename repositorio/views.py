import requests
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from repositorio.models import Repositorio
from repositorio.serializer import RepositorioSerializer
from repositorio.services import enviar_cadastro_aplicacao, cadastrar_aplicacao
from clientes.models import Cliente


class RepositorioView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        status_res = status.HTTP_200_OK

        if settings.SERVIDOR_CENTRAL:
            # Se é o servidor central, busca as aplicações de todos os clientes cadastrados nele
            # e retorna um dicionário com o id do cliente como chave e a lista de aplicações como valor.
            resposta = {}

            def trata_resposta_cliente(resposta_req):
                if resposta_req.status_code == 204:
                    return []
                elif resposta_req.status_code < 400:
                    return resposta_req.json()
                else:
                    return {'error': f'Erro ao buscar repositórios do cliente {cliente.nome}.'}

            if pk is None:
                clientes = Cliente.objects.all()

                for cliente in clientes:
                    res = requests.get(f'{cliente.url_base}/aplicacao/')
                    resposta[cliente.id] = trata_resposta_cliente(res)

            else:
                try:
                    cliente = get_object_or_404(Cliente, pk=pk)
                    res = requests.get(f'{cliente.url_base}/aplicacao/')
                    resposta = trata_resposta_cliente(res)

                except Http404:
                    resposta = {'error': 'Cliente não encontrado.'}
                    status_res = status.HTTP_404_NOT_FOUND

        else:
            if pk is None:
                repositorio = Repositorio.objects.all()

                if not repositorio:
                    resposta = []
                    status_res = status.HTTP_204_NO_CONTENT
                else:
                    serializer = RepositorioSerializer(repositorio, many=True)
                    resposta = serializer.data
            else:
                try:
                    aplicacao = get_object_or_404(Repositorio, pk=pk)
                    serializer = RepositorioSerializer(aplicacao)
                    resposta = serializer.data
                except Http404:
                    resposta = {'error': 'Aplicação não encontrada.'}
                    status_res = status.HTTP_404_NOT_FOUND

        return Response(resposta, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_400_BAD_REQUEST

        serializer = RepositorioSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            if settings.SERVIDOR_CENTRAL:
                assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
                cliente_id = request.data.get('cliente', None)

                cliente = Cliente.objects.get(id=cliente_id)
                status_res, resposta = enviar_cadastro_aplicacao(serializer, cliente)

            else:
                aplicacao = cadastrar_aplicacao(serializer)
                status_res = status.HTTP_201_CREATED
                resposta = {
                    'message': 'Aplicação cadastrada com sucesso.',
                    'aplicacao_id': aplicacao.id
                }

        except ValidationError as e:
            resposta = {'error': 'Dados inválidos.', 'details': e.detail}
            return Response(resposta, status=status_res)

        except AssertionError as e:
            resposta = e
            status_res = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            resposta = {'error': f'Erro ao tentar cadastrar aplicação: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res, content_type='application/json;charset=utf-8')

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            assert pk is not None, 'ID da aplicação obrigatória para método delete.'
            aplicacao = get_object_or_404(Repositorio, pk=pk)
            aplicacao.delete()

            status_res = status.HTTP_200_OK
            resposta = {'message': 'Aplicação deletada com sucesso.'}

        except AssertionError as e:
            resposta = {'error': str(e)}
            status_res = status.HTTP_400_BAD_REQUEST

        except Http404:
            resposta = {'error': 'Aplicação não encontrada.'}
            status_res = status.HTTP_404_NOT_FOUND

        except Exception as e:
            resposta = {'error': f'Erro ao tentar deletar aplicação: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res, content_type='application/json;charset=utf-8')