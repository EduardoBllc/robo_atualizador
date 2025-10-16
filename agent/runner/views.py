import traceback

from git.objects.commit import Commit
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.project.models import Project
from agent.runner.services import update
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
                if project.active_branch.name == (branch or project.branch_trunc):
                    try:
                        updated, new_head_commit = update(project)
                        response[project.id] = mount_response_for_project(project, updated, new_head_commit)
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())

            res_status = status.HTTP_200_OK

        return Response(response, status=res_status)
