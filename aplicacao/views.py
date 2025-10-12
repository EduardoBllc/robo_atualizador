import requests
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from aplicacao.models import Aplicacao
from aplicacao.serializer import AplicacaoSerializer
from aplicacao.services import enviar_cadastro_aplicacao, cadastrar_aplicacao
from clientes.models import Cliente


class AplicacaoView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        status_res = status.HTTP_200_OK

        if settings.SERVIDOR_CENTRAL:
            # Se é o servidor central, busca as aplicações de todos os clientes cadastrados nele
            # e retorna um dicionário com o id do cliente como chave e a lista de aplicações como valor.
            resposta = {}

            if pk is None:
                clientes = Cliente.objects.all()

                for cliente in clientes:
                    res = requests.get(f'{cliente.url_base}/aplicacao/')
                    if res.status_code == 204:
                        resposta[cliente.id] = []
                    elif res.status_code < 400:
                        resposta[cliente.id] = res.json()
                    else:
                        resposta[cliente.id] = {'error': f'Erro ao buscar aplicações do cliente {cliente.nome}.'}
            else:
                try:
                    cliente = get_object_or_404(Cliente, pk=pk)
                    res = requests.get(f'{cliente.url_base}/aplicacao/')
                    if res.status_code == 204:
                        resposta = []
                        status_res = status.HTTP_204_NO_CONTENT
                    elif res.status_code < 400:
                        resposta = res.json()
                    else:
                        resposta = {'error': f'Erro ao buscar aplicações do cliente {cliente.nome}.'}
                        status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
                except Http404:
                    resposta = {'error': 'Cliente não encontrado.'}
                    status_res = status.HTTP_404_NOT_FOUND

        else:
            if pk is None:
                aplicacoes = Aplicacao.objects.all()

                if not aplicacoes:
                    resposta = []
                    status_res = status.HTTP_204_NO_CONTENT
                else:
                    serializer = AplicacaoSerializer(aplicacoes, many=True)
                    resposta = serializer.data
            else:
                try:
                    aplicacao = get_object_or_404(Aplicacao, pk=pk)
                    serializer = AplicacaoSerializer(aplicacao)
                    resposta = serializer.data
                except Http404:
                    resposta = {'error': 'Aplicação não encontrada.'}
                    status_res = status.HTTP_404_NOT_FOUND

        return Response(resposta, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_400_BAD_REQUEST

        serializer = AplicacaoSerializer(data=request.data)

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
            aplicacao = get_object_or_404(Aplicacao, pk=pk)
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