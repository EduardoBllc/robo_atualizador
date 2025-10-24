import os
import git

from agent.project.models import Project

def check_remote(git_repo: git.Repo, remote: str = 'origin') -> bool:
    try:
        git_repo.remote(remote)
        return True
    except ValueError:
        return False


def fetch_remote(repository: git.Repo, remote: str = 'origin'):
    try:
        origin = repository.remote(remote)
        origin.fetch()
    except ValueError:
        raise ValueError(f'The remote {remote} does not exists.')


def switch_branch(git_repo: git.Repo, branch: str, remote: str | git.Remote = 'origin', only_local: bool = False):
    if isinstance(remote, git.Remote):
        remote = remote.name
    else:
        if not check_remote(git_repo, remote):
            raise ValueError(f'O repositório não possui um remote chamado {remote}.')

    if git_repo.active_branch == branch:
        return

    if branch in git_repo.branches:
        try:
            git_repo.git.checkout(branch)
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao trocar para branch {branch}: {str(e)}')
    else:
        remote_branch_name = f'{remote}/{branch}'

        if only_local or remote_branch_name not in git_repo.refs:
            raise ValueError(
                f'Branch {branch} não existe no repositório local{"." if only_local else "ou remoto."}'
            )

        try:
            git_repo.git.checkout('-b', branch, remote_branch_name)
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao trocar para branch {remote_branch_name}: {str(e)}')


def do_checkout(repository: git.Repo,
                hash_commit: str,
                remote: str = 'origin',
                after_fetch: bool = False):
    head_commit = repository.head.commit

    try:
        target_commit = repository.commit(hash_commit)

        if head_commit.hexsha == target_commit.hexsha:
            return False

        try:
            repository.git.checkout(target_commit.hexsha)
            return True
        except git.exc.GitCommandError as e:
            raise ValueError(f'Error checking out for commit {hash_commit}: {str(e)}')

    except git.exc.BadName:
        if after_fetch:
            raise ValueError(f'Commit {hash_commit} was not found.')

        fetch_remote(repository, remote)
        do_checkout(repository, hash_commit, remote, after_fetch=True)


def stash_push(repository: git.Repo):
    try:
        # Guardar quantidade de stashes antes de fazer o stash
        qty_stashes_before = len(repository.git.stash('list').splitlines())

        # Fazer stash das mudanças locais
        repository.git.stash('save', 'Auto-stash before update')

        # Verificar se o stash foi realmente criado
        qty_stashes_after = len(repository.git.stash('list').splitlines())

        return qty_stashes_after > qty_stashes_before
    except git.exc.GitCommandError as e:
        raise Exception(f'Erro pushing stash: {str(e)}')

def stash_pop(repository: git.Repo, identifier: str = None):
    try:
        if identifier:
            repository.git.stash('pop', identifier)
        else:
            repository.git.stash('pop')
    except git.exc.GitCommandError as e:
        raise Exception(f'Error applying stash: {str(e)}')


def update(project: Project, auto_stash: bool = True):
    updated = False

    repository_path = project.path
    remote = project.remote

    if not os.path.exists(repository_path):
        raise ValueError(f'The directory {repository_path} does not exists.')

    try:
        repository = git.Repo(repository_path)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError(f'The directory {repository_path} it\'s not a valid Git repository.')

    if not check_remote(repository, remote):
        raise ValueError(f'The remote {remote} does not exists.')

    did_stash = False

    try:
        if repository.is_dirty(untracked_files=True):
            if auto_stash:
                did_stash = stash_push(repository)
            else:
                raise AssertionError('Existem mudanças locais não comitadas. Por favor, faça commit ou stash antes de atualizar.')

        origin = repository.remote(remote)
        active_branch_name = repository.active_branch.name
        try:
            origin.pull(active_branch_name)
            # TODO: Verify if pull actually brought changes
            updated = True
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao fazer pull das últimas mudanças do branch {active_branch_name}: {str(e)}')
    finally:
        if did_stash:
            stash_pop(repository)

    if restart_command := project.restart_command:
        restart_command.execute()

    return updated, repository.head.commit
