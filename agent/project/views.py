import requests
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from agent.project.models import Project
from agent.project.serializer import ProjectSerializer
from agent.project.services import enviar_cadastro_repositorio, cadastrar_repositorio, get_projects_data
from central.agent.models import Agent


class ProjectView(APIView):
    def get(self, request: Request, *args, **kwargs):
        res_status = status.HTTP_200_OK

        projetos = Project.objects.all()

        if not projetos:
            response = []
        else:
            serializer = ProjectSerializer(projetos, many=True)
            response = serializer.data

        if not response:
            res_status = status.HTTP_204_NO_CONTENT

        return Response(response, status=res_status)

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            if settings.IS_CENTRAL:
                assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
                cliente_id = request.data.get('cliente', None)

                cliente = Agent.objects.get(id=cliente_id)
                res = requests.post(
                    f'{cliente.base_url}/repositorio/',
                    data=serializer.validated_data
                )

                status_res = res.status_code
                response = res.json()

            else:
                repositorio = cadastrar_repositorio(serializer)
                status_res = status.HTTP_201_CREATED
                response = {
                    'message': 'Repositório cadastrado com sucesso.',
                    'repositorio_id': repositorio.id
                }

        except ValidationError as e:
            response = {'error': 'Dados inválidos.', 'details': e.detail}
            status_res = status.HTTP_400_BAD_REQUEST

        except AssertionError as e:
            response = e
            status_res = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            response = {'error': f'Erro ao tentar cadastrar repositório: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=status_res, content_type='application/json;charset=utf-8')


class ProjectDetailsView(APIView):
    def get(self, request: Request, project_id: int = None):
        status_res = status.HTTP_200_OK

        try:
            project = get_object_or_404(Project, pk=project_id)
            serializer = ProjectSerializer(project)
            response = serializer.data
        except Http404:
            response = {'error': 'Project not found.'}
            status_res = status.HTTP_404_NOT_FOUND

        return Response(response, status=status_res)

    def delete(self, request, pk: int = None, *args, **kwargs):
        if settings.IS_CENTRAL:
            assert 'cliente' in request.data, 'Campo "cliente" obrigatório.'
            cliente_id = request.data.get('cliente', None)

            try:
                cliente = get_object_or_404(Agent, pk=cliente_id)
                res = requests.delete(f'{cliente.base_url}/repositorio/{pk}')

                if res.status_code < 400:
                    resposta = res.json()
                    status_res = res.status_code
                else:
                    resposta = {'error': f'Erro ao tentar deletar repositório no cliente {cliente.name}.'}
                    status_res = res.status_code

            except Http404:
                resposta = {'error': 'Cliente não encontrado.'}
                status_res = status.HTTP_404_NOT_FOUND

        else:
            try:
                assert pk is not None, 'ID do repositório obrigatório para método delete.'
                repositorio = get_object_or_404(Project, pk=pk)
                repositorio.delete()

                status_res = status.HTTP_200_OK
                resposta = {'message': 'Repositório deletado com sucesso.'}

            except AssertionError as e:
                resposta = {'error': str(e)}
                status_res = status.HTTP_400_BAD_REQUEST

            except Http404:
                resposta = {'error': 'Repositório não encontrado.'}
                status_res = status.HTTP_404_NOT_FOUND

            except Exception as e:
                resposta = {'error': f'Erro ao tentar deletar repositório: {e}'}
                status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res, content_type='application/json;charset=utf-8')
