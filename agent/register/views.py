import requests
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from agent.register.serializers import SelfRegisterSerializer


class SelfRegisterView(APIView):

    def get(self, request):
        # TODO: Verify if the agent is already registered, if so, return its details
        response = {'status': 'ok', 'message': 'Agent properly registered.'}
        res_status = status.HTTP_200_OK
        return Response(response, status=res_status)

    def post(self, request):
        serializer = SelfRegisterSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            # Calls central server to register this agent
            res_central = requests.post(url=f'{settings.CENTRAL_BASE_URL}/agent/', data=serializer.data)
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

        except ValidationError:
            response = {'error': 'Invalid data.', 'details': serializer.errors}
            res_status = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            response = {'error': 'Unexpected error.', 'details': str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)
