import git
import os

from agent.project.serializer import ProjectSerializer
from agent.project.models import Project


def register_project(serializer: ProjectSerializer):
    dados_serializados = serializer.validated_data

    repo_path = dados_serializados['path']

    if not os.path.exists(repo_path):
        raise AssertionError(f'The directory "{repo_path}" does not exists.')

    if os.path.isdir(repo_path) is False:
        raise AssertionError(f'The path "{repo_path}" is not a directory.')

    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        raise AssertionError(f'The directory {repo_path} is not a valid git repository.')

    remote = dados_serializados.get('remote', 'origin')
    if remote not in repo.remotes:
        raise AssertionError(f'Remote "{remote}" does not exists.')

    return serializer.save()


def modify_project(project: Project, data: dict):
    something_changed = False

    def _validate_path(path):
        if not os.path.exists(path):
            raise AssertionError(f'The directory "{path}" does not exists.')

        if os.path.isdir(path) is False:
            raise AssertionError(f'The path "{path}" is not a directory.')

        try:
            git.Repo(path)
        except git.exc.InvalidGitRepositoryError:
            raise AssertionError(f'The directory {path} is not a valid git repository.')

    def change_field(field_name):
        # Setting local variables for validation functions
        validate_path = _validate_path 

        if value := data.get(field_name):
            if getattr(project, field_name) == value:
                return

            setattr(project, field_name, value)
            nonlocal something_changed
            something_changed = True

            if validate_func := locals().get(f'validate_{field_name}'):
                validate_func(value)

    fields: tuple = ('path', 'name', 'auto_update')
    
    for field in fields:
        change_field(field)

    if something_changed:
        project.save()

    return something_changed