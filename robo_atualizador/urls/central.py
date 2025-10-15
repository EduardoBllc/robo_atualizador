from robo_atualizador.urls.base import urlpatterns
from django.urls import path

from core.views.status import CentralStatusView
from central.agent.views import AgentProjectsView, AgentView

urlpatterns += [
    path('status/', CentralStatusView.as_view(), name='status'),
    path('agent/', AgentView.as_view(), name='agent'),
    path('agent/<int:agent_id>/project/<int:project_id>/', AgentProjectsView.as_view(), name='agent-project'),
]