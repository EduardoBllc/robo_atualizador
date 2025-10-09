import os
import git

from aplicacao.models import Aplicacao

def verifica_remote(repositorio: git.Repo, remote: str = 'origin') -> bool:
    try:
        repositorio.remote(remote)
        return True
    except ValueError:
        return False

def alterar_branch(repositorio: git.Repo, branch: str, remote: str|git.Remote = 'origin'):
    if isinstance(remote, git.Remote):
        remote = remote.name
    else:
        if not verifica_remote(repositorio, remote):
            raise ValueError(f'O repositório não possui um remote chamado {remote}.')

    branch_atual = repositorio.active_branch

    if branch_atual == branch:
        return

    if branch in repositorio.branches:
        try:
            repositorio.git.checkout(branch)
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao trocar para branch {branch}: {str(e)}')
    else:
        # Verificar se o branch existe no remoto
        if f'{remote}/{branch}' not in repositorio.refs:
            raise ValueError(f'Branch {branch} não existe no repositório local ou remoto.')

        # Criar o branch local a partir do remoto
        try:
            repositorio.git.checkout('-b', branch, f'{remote}/{branch}')
        except git.exc.GitCommandError as e:
            raise ValueError(f'Erro ao trocar para branch {branch}: {str(e)}')


def atualiza_aplicacao(aplicacao: Aplicacao,
                       atualizar: bool = True,
                       branch: str = None,
                       hash_commit: str = None,
                       auto_stash: bool = True):

    diretorio_aplicacao = aplicacao.diretorio
    remote = aplicacao.remote

    if not os.path.exists(diretorio_aplicacao):
        raise ValueError(f'O diretório {diretorio_aplicacao} não existe.')

    try:
        repositorio = git.Repo(diretorio_aplicacao)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError(f'O diretório {diretorio_aplicacao} não é um repositório Git válido.')

    if not verifica_remote(repositorio, remote):
        raise ValueError(f'O repositório não possui um remote chamado {remote}.')

    realizou_stash = False

    try:
        # Passo 0: Verificar se há mudanças locais não comitadas
        if repositorio.is_dirty(untracked_files=True):
            if auto_stash:
                try:
                    # Guardar quantidade de stashes antes de fazer o stash
                    qtd_stashes_antes = len(repositorio.git.stash('list').splitlines())

                    # Fazer stash das mudanças locais
                    repositorio.git.stash('save', 'Auto-stash before update')

                    # Verificar se o stash foi realmente criado
                    qtd_stashes_depois = len(repositorio.git.stash('list').splitlines)

                    realizou_stash = qtd_stashes_depois > qtd_stashes_antes
                except git.exc.GitCommandError as e:
                    raise Exception(f'Erro ao fazer stash das mudanças locais: {str(e)}')
            else:
                raise AssertionError('Existem mudanças locais não comitadas. Por favor, faça commit ou stash antes de atualizar.')

        # Passo 1: Se "branch" foi fornecido, fazer checkout para o branch desejado
        if branch:
            alterar_branch(repositorio, branch)

        # Passo 2: Capturar o commit atual
        commit_atual = repositorio.head.commit
        commit_desejado = None

        # Passo 3: Procurar commit desejado (se fornecido) no estado atual do repositório
        if hash_commit:
            try:
                commit_desejado = repositorio.commit(hash_commit)
            except git.exc.BadName:
                if not atualizar:
                    raise ValueError(f'O commit {hash_commit} não foi encontrado no repositório local.')

            if commit_desejado:
                if commit_atual.hexsha != commit_desejado.hexsha:
                    #  Fazer checkout para o commit desejado
                    try:
                        repositorio.git.checkout(commit_desejado.hexsha)
                        return
                    except git.exc.GitCommandError as e:
                        raise ValueError(f'Erro ao realizar checkout para o commit {hash_commit}: {str(e)}')

        # Passo 4: Buscar atualizações do repositório remoto
        try:
            origin = repositorio.remote(remote)
            origin.fetch()
        except ValueError:
            raise ValueError('O repositório não possui um remoto chamado "origin".')

        # Passo 5: Se "hash_commit" foi fornecido, tentar encontrar o commit no repositório atualizado
        if hash_commit and not commit_desejado:
            try:
                commit_desejado = repositorio.commit(hash_commit)
            except git.exc.BadName:
                raise ValueError(f'O commit {hash_commit} não foi encontrado no repositório local ou remoto.')

            if commit_atual.hexsha != commit_desejado.hexsha:
                #  Fazer checkout para o commit desejado
                try:
                    repositorio.git.checkout(commit_desejado.hexsha)
                    return
                except git.exc.GitCommandError as e:
                    raise ValueError(f'Erro ao realizar checkout para o commit {hash_commit}: {str(e)}')

        # Passo 6: Se "atualizar" é True, fazer pull das últimas mudanças do branch atual
        if atualizar:
            branch_atual = repositorio.active_branch.name
            try:
                origin.pull(branch_atual)
            except git.exc.GitCommandError as e:
                raise ValueError(f'Erro ao fazer pull das últimas mudanças do branch {branch_atual}: {str(e)}')
    finally:
        if realizou_stash:
            try:
                repositorio.git.stash('pop')
            except git.exc.GitCommandError as e:
                raise Exception(f'Erro ao aplicar o stash de volta: {str(e)}')