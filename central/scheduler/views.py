import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404
from rest_framework.generics import get_object_or_404


class UpdateSchedulerView(APIView):
    def post(self, request, agent_id: int = None, project_id: int = None, *args, **kwargs):

        from central.agent.models import Agent

        branch: str = request.data.get('branch')

        try:
            if agent_id:
                agent = get_object_or_404(Agent, id=agent_id)

                url = f'{agent.base_url}/{f"project/{project_id}/" if project_id else ""}update/'

                agent_res = requests.post(url, data={'branch': branch})

                # Raise an error for bad responses (4xx and 5xx)
                agent_res.raise_for_status()

                response = agent_res.json()
                res_status = agent_res.status_code
            else:
                response = {}

                for agent in Agent.objects.all():
                    agent_res = requests.post(f'{agent.base_url}/update/', data={'branch': branch})
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