import git
import requests
import os

from requests import Response
from rest_framework.generics import get_object_or_404

from repositorio.models import Repositorio
from repositorio.serializer import RepositorioSerializer
from clientes.models import Cliente


def enviar_cadastro_repositorio(serializer: RepositorioSerializer, cliente: Cliente):
    resposta = requests.post(
        f'{cliente.url_base}/repositorio/',
        data=serializer.validated_data
    )

    return resposta.status_code, resposta.json()

def cadastrar_repositorio(serializer: RepositorioSerializer):
    dados_serializados = serializer.validated_data

    caminho_repositorio = dados_serializados['caminho']

    # Testa se o caminho enviado existe
    if not os.path.exists(caminho_repositorio):
        raise AssertionError(f'O caminho "{caminho_repositorio}" não existe.')

    # Testa se o caminho enviado é um repositório Git válido
    try:
        repo = git.Repo(caminho_repositorio)
    except git.exc.InvalidGitRepositoryError:
        raise AssertionError(f'O caminho {caminho_repositorio} não é um repositório Git válido.')

    # Testa se o remote existe no repositório
    remote = dados_serializados.get('remote', 'origin')
    if remote not in repo.remotes:
        raise AssertionError(f'O remote "{remote}" não existe no repositório.')

    # Testa se a branch existe no repositório
    branch_trunc = dados_serializados.get('branch_trunc', 'main')
    if branch_trunc not in repo.branches:
        raise AssertionError(f'A branch "{branch_trunc}" não existe no repositório.')


    return serializer.save()

def trata_resposta_cliente(resposta_req: Response, cliente: Cliente):
    if resposta_req.status_code == 204:
        return []
    elif resposta_req.status_code < 400:
        return resposta_req.json()
    else:
        return {'error': f'Erro ao buscar repositórios do cliente {cliente.nome}.'}

def get_todos_repositorios_clientes():
    # Chave: id do cliente
    # Valor: lista de repositórios
    repositorios = {}

    for cliente in Cliente.objects.all():
        res = requests.get(f'{cliente.url_base}/repositorio/')
        repositorios[cliente.id] = trata_resposta_cliente(res, cliente)

    return repositorios

def get_repositorio_cliente(cliente: Cliente, id_repositorio: int):
    res = requests.get(f'{cliente.url_base}/repositorio/{id_repositorio}/')
    return trata_resposta_cliente(res, cliente)


def get_todos_repositorios_locais():
    repositorio = Repositorio.objects.all()

    if not repositorio:
        return []
    else:
        serializer = RepositorioSerializer(repositorio, many=True)
        return serializer.data

def get_repositorio_local(id_repositorio: int):
    repositorio = get_object_or_404(Repositorio, pk=id_repositorio)
    serializer = RepositorioSerializer(repositorio)
    return serializer.data
