import requests
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from django.http import Http404

from central.agent.models import Agent
from central.agent.serializer import AgentSerializer, AgentProjectSerializer


class AgentView(APIView):

    def get(self, request):
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AgentSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            serialized_data = serializer.validated_data

            # Check if agent is reachable and if its status endpoint returns ok
            schema = 'https:' if serialized_data['uses_tls'] else 'http:'
            url = f'{schema}//{serialized_data["ip_address"]}:{serialized_data["port"]}/status/'

            res = requests.get(url, timeout=5)
            if res.status_code != 200:
                raise AssertionError(f'Status code not 200: {res.status_code}')

            if res.json().get('status') != 'ok':
                raise AssertionError('Status response is not ok')

            instance = serializer.save()
            resposta = {'message': 'Agent successfully registered.', 'agent_id': instance.id}

            status_res = status.HTTP_201_CREATED
        except ValidationError:
            resposta = {'error': 'Invalid data', 'details': serializer.errors}
            status_res = status.HTTP_400_BAD_REQUEST
        except AssertionError as e:
            resposta = {'error': str(e)}
            status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            resposta = {'error': str(e)}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(resposta, status=status_res)


class AgentProjectsView(APIView):

    def get(self, request, agent_id=None, project_id=None, *args, **kwargs):
        res_status = status.HTTP_200_OK

        try:
            response = {}

            agents_qs = Agent.objects.all()

            if agent_id:
                agents_qs = agents_qs.filter(agent_id=agent_id)

            for agent in agents_qs:
                url = f'{agent.base_url}/project/'

                if project_id:
                    url += f'{project_id}/'

                res = requests.get(url)

                if res.status_code == 204:
                    response[agent.id] = []
                elif res.status_code < 400:
                    response[agent.id] = res.json()
                else:
                    response[agent.id] = {'error': f'Agent\'s project not found.'}

            if not response:
                res_status = status.HTTP_204_NO_CONTENT

        except Agent.DoesNotExist:
            response = {'error': 'Agent not found.'}
            res_status = status.HTTP_404_NOT_FOUND
        except Exception as e:
            response = {'error': str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)

    def post(self, request, agent_id: int, *args, **kwargs):
        serializer = AgentProjectSerializer(data=request.data)

        try:
            # Validate incoming data
            serializer.is_valid(raise_exception=True)

            agent = get_object_or_404(Agent, pk=agent_id)
            # Calls agent to register the project
            res = requests.post(f'{agent.base_url}/project/', data=serializer.data)
            # Raise an error for bad responses
            res.raise_for_status()

            status_res = res.status_code
            response = res.json()

        except ValidationError as e:
            response = {'error': 'Invalid data', 'details': e.detail}
            status_res = status.HTTP_400_BAD_REQUEST
        except Http404:
            response = {'error': 'Agent not found.'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            response = {'error': str(e)}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=status_res, content_type='application/json;charset=utf-8')

    def delete(self, request, agent_id: int, project_id: int, *args, **kwargs):

        try:
            agent = get_object_or_404(Agent, pk=agent_id)
            res = requests.delete(f'{agent.base_url}/projects/{project_id}/')

            if res.status_code < 400:
                response = res.json()
                res_status = res.status_code
            else:
                response = {'error': f'Erro ao tentar deletar repositório no cliente {agent.name}.'}
                res_status = res.status_code

        except Http404:
            response = {'error': 'Agent not found.'}
            res_status = status.HTTP_404_NOT_FOUND
        except Exception as e:
            response = {'error': str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)
