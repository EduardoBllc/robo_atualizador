import requests
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from repositorio.models import Repositorio
from repositorio.serializer import RepositorioSerializer
from repositorio.services import enviar_cadastro_repositorio, cadastrar_repositorio, get_todos_repositorios_clientes, \
    get_repositorio_cliente, get_todos_repositorios_locais, get_repositorio_local
from clientes.models import Cliente


class RepositorioView(APIView):
    def get(self, request: Request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        if settings.IS_CENTRAL:
            resposta = get_todos_repositorios_clientes()

        else:
            resposta = get_todos_repositorios_locais()

            if not resposta:
                status_res = status.HTTP_204_NO_CONTENT

        return Response(resposta, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_400_BAD_REQUEST

        serializer = RepositorioSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            if settings.IS_CENTRAL:
                assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
                cliente_id = request.data.get('cliente', None)

                cliente = Cliente.objects.get(id=cliente_id)
                status_res, resposta = enviar_cadastro_repositorio(serializer, cliente)

            else:
                repositorio = cadastrar_repositorio(serializer)
                status_res = status.HTTP_201_CREATED
                resposta = {
                    'message': 'Repositório cadastrado com sucesso.',
                    'repositorio_id': repositorio.id
                }

        except ValidationError as e:
            resposta = {'error': 'Dados inválidos.', 'details': e.detail}
            return Response(resposta, status=status_res)

        except AssertionError as e:
            resposta = e
            status_res = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            resposta = {'error': f'Erro ao tentar cadastrar repositório: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res, content_type='application/json;charset=utf-8')


class RepositorioDetailsView(APIView):
    def get(self, request: Request, pk: int = None, *args, **kwargs):
        status_res = status.HTTP_200_OK

        if settings.IS_CENTRAL:
            # Se é o servidor central, busca as aplicações de todos os clientes cadastrados nele
            # e retorna um dicionário com o id do cliente como chave e a lista de aplicações como valor.
            try:
                assert 'cliente' in request.query_params, 'Parâmetro "cliente" obrigatório.'
                cliente_id = request.query_params.get('cliente', None)
                cliente = get_object_or_404(Cliente, pk=cliente_id)
                resposta = get_repositorio_cliente(cliente=cliente, id_repositorio=pk)
            except AssertionError as e:
                resposta = {'error': str(e)}
                status_res = status.HTTP_400_BAD_REQUEST
        else:
            try:
                resposta = get_repositorio_local(id_repositorio=pk)
            except Http404:
                resposta = {'error': 'Repositório não encontrado.'}
                status_res = status.HTTP_404_NOT_FOUND

        return Response(resposta, status=status_res)

    def delete(self, request, pk: int = None, *args, **kwargs):
        if settings.IS_CENTRAL:
            assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
            cliente_id = request.data.get('cliente', None)

            try:
                cliente = get_object_or_404(Cliente, pk=cliente_id)
                res = requests.delete(f'{cliente.url_base}/repositorio/{pk}')

                if res.status_code < 400:
                    resposta = res.json()
                    status_res = res.status_code
                else:
                    resposta = {'error': f'Erro ao tentar deletar repositório no cliente {cliente.nome}.'}
                    status_res = res.status_code

            except Http404:
                resposta = {'error': 'Cliente não encontrado.'}
                status_res = status.HTTP_404_NOT_FOUND

        else:
            try:
                assert pk is not None, 'ID do repositório obrigatório para método delete.'
                repositorio = get_object_or_404(Repositorio, pk=pk)
                repositorio.delete()

                status_res = status.HTTP_200_OK
                resposta = {'message': 'Repositório deletado com sucesso.'}

            except AssertionError as e:
                resposta = {'error': str(e)}
                status_res = status.HTTP_400_BAD_REQUEST

            except Http404:
                resposta = {'error': 'Repositório não encontrado.'}
                status_res = status.HTTP_404_NOT_FOUND

            except Exception as e:
                resposta = {'error': f'Erro ao tentar deletar repositório: {e}'}
                status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res, content_type='application/json;charset=utf-8')
