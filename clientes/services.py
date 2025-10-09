import requests

from django.conf import settings

from rest_framework import status

from clientes.serializer import ClienteSerializer
from utils.objects import Central


def envia_cadastro_cliente_central(serializer: ClienteSerializer):
    # Chamar API da central para cadastrar o cliente
    url = Central.get_url_base() + '/cliente/'
    body = {
        "descricao": serializer.validated_data['descricao'],
        "ip": serializer.validated_data['ip'],
        "porta": serializer.validated_data['porta'],
        "usa_tls": serializer.validated_data['usa_tls'],
    }

    try:
        res_central = requests.post(url=url, data=body)
        res_central.raise_for_status()
        return res_central.status_code, res_central.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f'Erro HTTP ao tentar conectar na central: {e}') from e
    except requests.exceptions.RequestException as e:
        raise Exception(f'Erro ao tentar conectar na central: {e}') from e

def cadastra_cliente(serializer: ClienteSerializer):
    dados_serializados = serializer.validated_data

    # Realizar requisição de status para garantir que o cliente está acessível
    protocolo = 'https:' if dados_serializados['usa_tls'] else 'http:'
    url = f'{protocolo}//{dados_serializados["ip"]}:{dados_serializados["porta"]}/status/'

    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            raise Exception('Status code diferente de 200')
        status_ok = res.json().get('status') == 'ok'
    except Exception as e:
        status_ok = False

    if status_ok:
        instance = serializer.save()
        status_res = status.HTTP_201_CREATED
        resposta = {'message': 'Cliente cadastrado com sucesso.', 'cliente_id': instance.id}
    else:
        status_res = status.HTTP_400_BAD_REQUEST
        resposta = {'error': 'Não foi possível acessar clietne.'}

    return status_res, resposta
