import git
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from aplicacao.serializer import AplicacaoSerializer
from aplicacao.services import enviar_cadastro_aplicacao, cadastrar_aplicacao
from clientes.models import Cliente


class AplicacaoView(APIView):
    allowed_methods = ['get', 'post']

    def get(self, request):
        if settings.SERVIDOR_CENTRAL:
            # Retorna todas as aplicações disponíveis de todos os clientes
            pass
        else:
            # Retorna todas as aplicações disponíveis deste cliente
            pass
        return Response({"message": "Hello, World!"}, status=status.HTTP_200_OK)

    def post(self, request):
        status_res = status.HTTP_400_BAD_REQUEST

        serializer = AplicacaoSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            if settings.SERVIDOR_CENTRAL:
                assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
                cliente_id = request.data.get('cliente', None)

                cliente = Cliente.objects.get(id=cliente_id)
                status_res, resposta = enviar_cadastro_aplicacao(serializer, cliente)

            else:
                aplicacao = cadastrar_aplicacao(serializer)
                status_res = status.HTTP_201_CREATED
                resposta = {
                    'message': 'Aplicação cadastrada com sucesso.',
                    'aplicacao_id': aplicacao.id
                }

        except ValidationError as e:
            resposta = {'error': 'Dados inválidos.', 'details': e.detail}
            return Response(resposta, status=status_res)

        except git.exc.InvalidGitRepositoryError:
            caminho = request.data.get('caminho', '')
            resposta = {'error': f'{caminho} não é um repositório git válido.'}
            status_res = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            resposta = {'error': f'Erro ao tentar cadastrar aplicação: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res)