import git
import requests

from aplicacao.serializer import AplicacaoSerializer
from clientes.models import Cliente


def enviar_cadastro_aplicacao(serializer: AplicacaoSerializer, cliente: Cliente):
    resposta = requests.post(
        f'{cliente.url_base}/aplicacao/',
        data=serializer.validated_data
    )

    return resposta.status_code, resposta.json()

def cadastrar_aplicacao(serializer: AplicacaoSerializer):
    dados_serializados = serializer.validated_data

    # Testa se o caminho enviado é realmente um diretório git
    caminho_aplicacao = dados_serializados['caminho']

    # Testar se o caminho enviado é um repositório git válido
    git.Repo(caminho_aplicacao)

    return serializer.save()
