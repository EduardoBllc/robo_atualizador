import git
import requests
import os

from repositorio.serializer import RepositorioSerializer
from clientes.models import Cliente


def enviar_cadastro_aplicacao(serializer: RepositorioSerializer, cliente: Cliente):
    resposta = requests.post(
        f'{cliente.url_base}/aplicacao/',
        data=serializer.validated_data
    )

    return resposta.status_code, resposta.json()

def cadastrar_aplicacao(serializer: RepositorioSerializer):
    dados_serializados = serializer.validated_data

    caminho_aplicacao = dados_serializados['caminho']

    # Testa se o caminho enviado existe
    if not os.path.exists(caminho_aplicacao):
        raise AssertionError(f'O caminho "{caminho_aplicacao}" não existe.')

    # Testa se o caminho enviado é um repositório Git válido
    try:
        repo = git.Repo(caminho_aplicacao)
    except git.exc.InvalidGitRepositoryError:
        raise AssertionError(f'O caminho {caminho_aplicacao} não é um repositório Git válido.')

    # Testa se o remote existe no repositório
    remote = dados_serializados.get('remote', 'origin')
    if remote not in repo.remotes:
        raise AssertionError(f'O remote "{remote}" não existe no repositório.')

    # Testa se a branch existe no repositório
    branch_trunc = dados_serializados.get('branch_trunc', 'main')
    if branch_trunc not in repo.branches:
        raise AssertionError(f'A branch "{branch_trunc}" não existe no repositório.')


    return serializer.save()
