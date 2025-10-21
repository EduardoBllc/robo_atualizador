from django.urls import path
from core.views.migrations import MigrationsView

urlpatterns = [
    path('migrate/', MigrationsView.as_view(), name='run-migrations')
]
