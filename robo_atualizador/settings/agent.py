"""
Settings for the Agent (client) role.
"""
from .base import *

import os

CENTRAL_HOST = os.environ.get('CENTRAL_HOST')
CENTRAL_PORT = os.environ.get('CENTRAL_PORT')
CENTRAL_USES_TLS = os.environ.get('CENTRAL_USES_TLS', '0') in ('1', 'true', 'True')

if not (CENTRAL_HOST and CENTRAL_PORT):
    raise Exception("Variáveis de ambiente CENTRAL_HOST e CENTRAL_PORT são obrigatórias para aplicações.")
