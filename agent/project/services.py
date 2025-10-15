import git
import requests
import os

from requests import Response
from rest_framework.generics import get_object_or_404

from agent.project.models import Project
from agent.project.serializer import ProjectSerializer
from central.agent.models import Agent


def enviar_cadastro_repositorio(serializer: ProjectSerializer, cliente: Agent):
    resposta = requests.post(
        f'{cliente.base_url}/repositorio/',
        data=serializer.validated_data
    )

    return resposta.status_code, resposta.json()

def cadastrar_repositorio(serializer: ProjectSerializer):
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

