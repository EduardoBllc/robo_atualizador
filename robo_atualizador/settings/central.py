"""
Settings for the Central (master) role.
"""
from .base import *

INSTALLED_APPS += [
    "central.agent",
    "central.scheduler",
]