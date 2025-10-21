from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

def run_migrations(app: str = None):
    if app:
        call_command("migrate", aap_label=app, interactive=False, verbosity=1)
    else:
        call_command("migrate", interactive=False, verbosity=1)

class MigrationsView(APIView):
    """
    View para aplicar migrations pendentes.
    """

    def post(self, request, *args, **kwargs):
        app = request.data.get("app", None)

        try:
            run_migrations(app=app)
            response = {"status": "Migrations applied successfully."}
            res_status = status.HTTP_200_OK
        except CommandError as e:
            response = {"error": str(e)}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        except Exception as e:
            response = {"error": f"An unexpected error occurred: {str(e)}"}
            res_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=res_status)
