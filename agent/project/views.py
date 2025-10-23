from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.project.models import Project
from agent.project.serializer import ProjectSerializer
from agent.project.services import modify_project, register_project


class ProjectView(APIView):
    def get(self, request: Request, *args, **kwargs):
        res_status = status.HTTP_200_OK

        projects = Project.objects.all()

        if not projects:
            response = []
        else:
            serializer = ProjectSerializer(projects, many=True)
            response = serializer.data

        if not response:
            res_status = status.HTTP_204_NO_CONTENT

        return Response(response, status=res_status)

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            project = register_project(serializer)
            status_res = status.HTTP_201_CREATED
            response = {
                'message': 'Project successfull registered.',
                'project_id': project.id
            }

        except ValidationError as e:
            response = {'error': 'Invalid data.', 'details': e.detail}
            status_res = status.HTTP_400_BAD_REQUEST

        except AssertionError as e:
            response = {'error': str(e)}
            status_res = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            response = {'error': f'Erro ao tentar cadastrar repositório: {e}'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=status_res, content_type='application/json;charset=utf-8')
    
    def patch(self, request, *args, **kwargs):
        data = request.data

        try:
            assert 'id' in data, 'Project "id" is required'
            project_id = data['id']

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                raise AssertionError(f'Project ID {project_id} not found')

            modified = modify_project(project, data)
            response_message = 'Project successfull modified' if modified else 'Nothing changed'

            response = {'message': response_message}
            res_status = status.HTTP_200_OK

        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {'error': str(e)}

        return Response(response, status=res_status)


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

    def delete(self, request, project_id: int, *args, **kwargs):
        try:
            project = get_object_or_404(Project, pk=project_id)
            project.delete()

            res_status = status.HTTP_200_OK
            response = {'message': 'Repositório deletado com sucesso.'}

        except AssertionError as e:
            response = {'error': str(e)}
            res_status = status.HTTP_400_BAD_REQUEST

        except Http404:
            response = {'error': 'Repositório não encontrado.'}
            res_status = status.HTTP_404_NOT_FOUND

        except Exception as e:
            response = {'error': f'Erro ao tentar deletar repositório: {e}'}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status, content_type='application/json;charset=utf-8')
    
    def patch(self, request, project_id: int, *args, **kwargs):
        data = request.data.copy()

        try:
            try:
                project = get_object_or_404(Project, id=project_id)
            except Project.DoesNotExist:
                raise AssertionError(f'Project ID {project_id} not found')

            modified = modify_project(project, data)
            response_message = 'Project successfull modified' if modified else 'Nothing changed'

            response = {'message': response_message}
            res_status = status.HTTP_200_OK

        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {'error': str(e)}

        return Response(response, status=res_status)
