import requests
from django.conf import settings
from git.objects.commit import Commit
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.project import Project
from central.agent.models import Agent
from atualizacao.services import update
from django.http import Http404
from rest_framework.generics import get_object_or_404


class UpdateRunnerView(APIView):
    def post(self, request, project_id: int = None, *args, **kwargs):
        """
        Endpoint para iniciar o processo de atualização.

        Params:
        - branch: nome do branch que recebeu atualização. Só serà enviada atualização para as aplicações que estão com
        essa branch ativa.
        """

        def mount_response_for_project(proj: Project, upd: bool, commit: Commit) -> dict:
            if update:
                message = f'Project {project.name} successfully updated.'
            else:
                message = f'Project {project.name} is already up to date.'

            return {
                'message': message,
                'updated': upd,
                'head_commit': {
                    'hash': commit.hexsha,
                    'date': commit.committed_datetime,
                    'message': commit.message,
                    'author': str(commit.author),
                },
            }

        branch: str = request.data.get('branch')
        if project_id:
            project = get_object_or_404(Project, id=project_id)

            if project.active_branch.name == branch:
                updated, head_commit = update(project)

                response = mount_response_for_project(project, updated, head_commit)
            else:
                response = {'message': f'Project {project.name} active branch is not {branch}.'}

            res_status = status.HTTP_200_OK

        else:
            response = {}

            for project in Project.objects.all():
                if project.active_branch.name == branch:
                    updated, new_head_commit = update(project)
                    response[project.id] = mount_response_for_project(project, updated, new_head_commit)

            res_status = status.HTTP_200_OK

        return Response(response, status=res_status)


class UpdateCallerView(APIView):
    def post(self, request, agent_id: int = None, project_id: int = None, *args, **kwargs):
        branch: str = request.data.get('branch')

        try:
            if agent_id:
                agent = get_object_or_404(Agent, id=agent_id)

                url = f'{agent.base_url}/update/'

                if project_id:
                    url = f'{url}{project_id}/'

                agent_res = requests.post(url, timeout=10, data={'branch': branch})

                # Raise an error for bad responses (4xx and 5xx)
                agent_res.raise_for_status()

                response = agent_res.json()
                res_status = agent_res.status_code
            else:
                response = {}

                for agent in Agent.objects.all():
                    agent_res = requests.post(f'{agent.base_url}/update/', timeout=10, data={'branch': branch})
                    response[agent.id] = {
                        'status': agent_res.status_code,
                        'response': agent_res.json(),
                    }

                res_status = status.HTTP_200_OK

        except Http404:
            response = {'error': 'Agent not found.'}
            res_status = status.HTTP_404_NOT_FOUND
        except requests.exceptions.HTTPError as e:
            response = {'error': f'HTTP error occurred: {str(e)}'}
            res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            response = {'error': str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)


