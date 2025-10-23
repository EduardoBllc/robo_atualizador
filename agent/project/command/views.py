from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404


class CommandView(APIView):

    def get(self, request, project_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command
        from agent.project.command.serializer import CommandSerializer

        data = request.query_params

        try:
            project = get_object_or_404(Project, id=project_id)
            if 'id' in data:
                command_id = data.get('id')

                try:
                    command = project.commands.get(id=command_id)
                except Command.DoesNotExist:
                    raise AssertionError(f"Command ID {command_id} not found for the given project.")

                response = CommandSerializer(command).data
            else:
                commands = project.commands.all()
                response = CommandSerializer(commands, many=True).data

            res_status = status.HTTP_200_OK
        except Http404:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": "Project not found."}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)

    def post(self, request, project_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.serializer import CommandSerializer

        try:
            project = get_object_or_404(Project, id=project_id)

            data = request.data.copy()
            data['project'] = project.id

            serializer = CommandSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            response = {'message': 'Command created successfully.', 'command_id': instance.id}
            res_status = status.HTTP_200_OK
        except Http404:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": "Project not found."}
        except ValidationError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": 'Invalid data.', "details": e.detail}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)

    def patch(self, request, project_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command
        from agent.project.command.services import modify_command

        data = request.data

        try:
            project = get_object_or_404(Project, id=project_id)

            assert 'id' in request.data, 'Command "id" is required'
            command_id = data.get('id')

            try:
                command = Command.objects.get(id=command_id, project=project)
            except Command.DoesNotExist:
                raise AssertionError("Command not found for the given project.")

            modified = modify_command(command, data)

            response = {'message': 'Command successfully updated' if modified else 'Nothing changed'}
            res_status = status.HTTP_200_OK

        except Http404:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": "Project not found."}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)

    def delete(self, request, project_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command

        data = request.data

        try:
            project = get_object_or_404(Project, id=project_id)

            assert 'id' in request.data, 'Command "id" is required'
            command_id = data.get('id')

            try:
                command = Command.objects.get(id=command_id, project=project)
            except Command.DoesNotExist:
                raise AssertionError("Command not found for the given project.")

            command.delete()

            response = {'message': 'Command successfully deleted'}
            res_status = status.HTTP_200_OK

        except Http404:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": "Project not found."}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)


class CommandDetailsView(APIView):

    def get(self, request, project_id: int, command_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command
        from agent.project.command.serializer import CommandSerializer

        try:
            try:
                project = get_object_or_404(Project, id=project_id)
            except Http404:
                raise Http404("Project not found.")

            try:
                command = get_object_or_404(Command, id=command_id, project=project)
            except Http404:
                raise Http404("Command not found for the given project.")

            response = CommandSerializer(command).data
            res_status = status.HTTP_200_OK
        except Http404 as e:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": str(e)}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)

    def patch(self, request, project_id: int, command_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command
        from agent.project.command.services import modify_command

        data = request.data

        try:
            try:
                project = get_object_or_404(Project, id=project_id)
            except Http404:
                raise Http404("Project not found.")

            try:
                command = get_object_or_404(Command, id=command_id, project=project)
            except Http404:
                raise Http404("Command not found for the given project.")

            modified = modify_command(command, data)

            response = {'message': 'Command successfully updated' if modified else 'Nothing changed'}
            res_status = status.HTTP_200_OK

        except Http404 as e:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": str(e)}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)

    def delete(self, request, project_id: int, command_id: int, *args, **kwargs):
        from agent.project.models import Project
        from agent.project.command.models import Command

        try:
            try:
                project = get_object_or_404(Project, id=project_id)
            except Http404:
                raise Http404("Project not found")

            try:
                command = get_object_or_404(Command, id=command_id, project=project)
            except Http404:
                raise Http404("Command not found for the given project")

            command.delete()

            response = {'message': 'Command successfully deleted'}
            res_status = status.HTTP_200_OK

        except Http404 as e:
            res_status = status.HTTP_404_NOT_FOUND
            response = {"error": str(e)}
        except AssertionError as e:
            res_status = status.HTTP_400_BAD_REQUEST
            response = {"error": str(e)}
        except Exception as e:
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"error": "An unexpected error occurred.", "details": str(e)}

        return Response(response, status=res_status)
