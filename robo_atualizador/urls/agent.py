from robo_atualizador.urls.base import urlpatterns
from django.urls import path

from core.views.status import AgentStatusView
from agent.project.views import ProjectView, ProjectDetailsView
from agent.runner.views import UpdateRunnerView

from agent.register.views import SelfRegisterView
from agent.project.command.views import CommandDetailsView, CommandView

urlpatterns += [
    path("status/", AgentStatusView.as_view(), name='status'),
    path("project/", ProjectView.as_view(), name='project'),
    path("project/<int:project_id>/", ProjectDetailsView.as_view(), name="project-detail"),
    path("update/", UpdateRunnerView.as_view(), name="update-runner"),
    path("project/<int:project_id>/update/", UpdateRunnerView.as_view(), name="project-update"),
    path("register/", SelfRegisterView.as_view(), name='self-register'),
    path("project/<int:project_id>/command/", CommandView.as_view(), name='command'),
    path("project/<int:project_id>/command/<int:command_id>/", CommandDetailsView.as_view(), name='command-detail'),
]