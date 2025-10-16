import requests
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class SelfRegisterView(APIView):

    def get(self, request):
        ip_params = request.query_params.get('ip_address')
        port_params = request.query_params.get('port')

        query_params = {
            'ip_address': ip_params or settings.AGENT_HOST,
            'port': port_params or settings.AGENT_PORT,
        }

        central_res = requests.get(f'{settings.CENTRAL_BASE_URL}/agent/', params=query_params)
        central_res_status = central_res.status_code

        if central_res_status == 200:
            response = {'status': 'ok', 'message': 'Agent properly registered.'}
            res_status = status.HTTP_200_OK
        elif central_res_status == 404:
            response = {'status': 'not_registered', 'message': 'Agent not registered.'}
            res_status = status.HTTP_404_NOT_FOUND
        else:
            response = {'status': 'error', 'message': 'Error checking registration status.', 'details': central_res.text}
            res_status = status.HTTP_502_BAD_GATEWAY

        return Response(response, status=res_status)

    def post(self, request):
        try:
            print(request.data)
            assert 'name' in request.data, "Agent 'name' is required."

            agent_name = request.data['name']
            ip_params = request.data.get('ip')
            port_params = request.data.get('port')
            uses_tls_params = request.data.get('uses_tls')

            assert ip_params or settings.AGENT_HOST, "Agent 'ip' is required."

            data = {
                'name': agent_name,
                'ip_address': ip_params or settings.AGENT_HOST,
                'port': port_params or settings.AGENT_PORT,
                'uses_tls': uses_tls_params or settings.AGENT_USES_TLS,
            }

            # Calls central server to register this agent
            res_central = requests.post(url=f'{settings.CENTRAL_BASE_URL}/agent/', data=data)
            # Raise an error for bad responses
            res_central.raise_for_status()

            res_status = res_central.status_code
            response = res_central.json()

        except requests.exceptions.HTTPError as e:
            response = {'error': str(e)}
            res_status = status.HTTP_502_BAD_GATEWAY

        except requests.exceptions.RequestException as e:
            response = {'error': str(e)}
            res_status = status.HTTP_502_BAD_GATEWAY

        except AssertionError as e:
            response = {'error': str(e)}
            res_status = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            response = {'error': 'Unexpected error.', 'details': str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)
