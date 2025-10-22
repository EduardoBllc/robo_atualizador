import git
import os

from agent.project.serializer import ProjectSerializer


def register_project(serializer: ProjectSerializer):
    dados_serializados = serializer.validated_data

    caminho_repositorio = dados_serializados['path']

    if not os.path.exists(caminho_repositorio):
        raise AssertionError(f'The directory "{caminho_repositorio}" does not exists.')

    if os.path.isdir(caminho_repositorio) is False:
        raise AssertionError(f'The path "{caminho_repositorio}" is not a directory.')

    try:
        repo = git.Repo(caminho_repositorio)
    except git.exc.InvalidGitRepositoryError:
        raise AssertionError(f'The directory {caminho_repositorio} is not a valid git repository.')

    remote = dados_serializados.get('remote', 'origin')
    if remote not in repo.remotes:
        raise AssertionError(f'Remote "{remote}" does not exists.')

    return serializer.save()
