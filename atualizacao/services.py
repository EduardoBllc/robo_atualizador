import os
import git

from agent.project import Project

def check_remote(git_repo: git.Repo, remote: str = 'origin') -> bool:
    try:
        git_repo.remote(remote)
        return True
    except ValueError:
        return False

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

        # Verificar se o branch existe no remoto
        if only_local or remote_branch_name not in git_repo.refs:
            raise ValueError(
                f'Branch {branch} não existe no repositório local{"." if only_local else "ou remoto."}'
            )

        # Criar o branch local a partir do remoto
        try:
            git_repo.git.checkout('-b', branch, remote_branch_name)
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao trocar para branch {remote_branch_name}: {str(e)}')


def update(repository: Project,
           atualizar: bool = True,
           branch: str = None,
           hash_commit: str = None,
           auto_stash: bool = True):

    repository_path = repository.path
    remote = repository.remote

    if not os.path.exists(repository_path):
        raise ValueError(f'O diretório {repository_path} não existe.')

    try:
        git_repository = git.Repo(repository_path)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError(f'O diretório {repository_path} não é um repositório Git válido.')

    if not check_remote(git_repository, remote):
        raise ValueError(f'O repositório não possui um remote chamado {remote}.')

    did_stash = False

    try:
        # Passo 0: Verificar se há mudanças locais não comitadas
        if git_repository.is_dirty(untracked_files=True):
            if auto_stash:
                try:
                    # Guardar quantidade de stashes antes de fazer o stash
                    qty_stashes_before = len(git_repository.git.stash('list').splitlines())

                    # Fazer stash das mudanças locais
                    git_repository.git.stash('save', 'Auto-stash before update')

                    # Verificar se o stash foi realmente criado
                    qty_stashes_after = len(git_repository.git.stash('list').splitlines)

                    did_stash = qty_stashes_after > qty_stashes_before
                except git.exc.GitCommandError as e:
                    raise Exception(f'Erro ao fazer stash das mudanças locais: {str(e)}')
            else:
                raise AssertionError('Existem mudanças locais não comitadas. Por favor, faça commit ou stash antes de atualizar.')

        # Passo 1: Se "branch" foi fornecido, fazer checkout para o branch desejado
        if branch:
            switch_branch(git_repository, branch)

        # Passo 2: Capturar o commit atual
        commit_atual = git_repository.head.commit
        commit_desejado = None

        # Passo 3: Procurar commit desejado (se fornecido) no estado atual do repositório
        if hash_commit:
            try:
                commit_desejado = git_repository.commit(hash_commit)
            except git.exc.BadName:
                if not atualizar:
                    raise ValueError(f'O commit {hash_commit} não foi encontrado no repositório local.')

            if commit_desejado:
                if commit_atual.hexsha != commit_desejado.hexsha:
                    #  Fazer checkout para o commit desejado
                    try:
                        git_repository.git.checkout(commit_desejado.hexsha)
                        return
                    except git.exc.GitCommandError as e:
                        raise ValueError(f'Erro ao realizar checkout para o commit {hash_commit}: {str(e)}')

        # Passo 4: Buscar atualizações do repositório remoto
        try:
            origin = git_repository.remote(remote)
            origin.fetch()
        except ValueError:
            raise ValueError('O repositório não possui um remoto chamado "origin".')

        # Passo 5: Se "hash_commit" foi fornecido, tentar encontrar o commit no repositório atualizado
        if hash_commit and not commit_desejado:
            try:
                commit_desejado = git_repository.commit(hash_commit)
            except git.exc.BadName:
                raise ValueError(f'O commit {hash_commit} não foi encontrado no repositório local ou remoto.')

            if commit_atual.hexsha != commit_desejado.hexsha:
                #  Fazer checkout para o commit desejado
                try:
                    git_repository.git.checkout(commit_desejado.hexsha)
                    return
                except git.exc.GitCommandError as e:
                    raise ValueError(f'Erro ao realizar checkout para o commit {hash_commit}: {str(e)}')

        # Passo 6: Se "atualizar" é True, fazer pull das últimas mudanças do branch atual
        if atualizar:
            branch_atual = git_repository.active_branch.name
            try:
                origin.pull(branch_atual)
            except git.exc.GitCommandError as e:
                raise ValueError(f'Erro ao fazer pull das últimas mudanças do branch {branch_atual}: {str(e)}')
    finally:
        if did_stash:
            try:
                git_repository.git.stash('pop')
            except git.exc.GitCommandError as e:
                raise Exception(f'Erro ao aplicar o stash de volta: {str(e)}')

    # TODO: Verify if there were changes after pull
    return True, git_repository.head.commit
