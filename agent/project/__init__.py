# Avoid importing models at package import time. Import models from `agent.project.models`
# only inside functions or modules that run after Django apps are loaded.
# This prevents AppRegistryNotReady during app loading.

# from .models import Project

