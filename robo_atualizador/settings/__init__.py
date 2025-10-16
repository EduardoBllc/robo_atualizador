import importlib
import os
from django.core.exceptions import ImproperlyConfigured

ROLE = os.getenv("ROLE", "agent").strip().lower()

MODULE_BY_ROLE = {
    "agent": "robo_atualizador.settings.agent",
    "central": "robo_atualizador.settings.central",
}

if ROLE not in MODULE_BY_ROLE:
    valid = ", ".join(MODULE_BY_ROLE.keys())
    raise ImproperlyConfigured(f"ROLE inválido: '{ROLE}'. Valores válidos: {valid}")

_selected = MODULE_BY_ROLE[ROLE]
_mod = importlib.import_module(_selected)

# Exporta apenas constantes UPPERCASE do módulo selecionado
for _name in dir(_mod):
    if _name.isupper():
        globals()[_name] = getattr(_mod, _name)

# Metadados úteis para diagnóstico
SELECTED_SETTINGS_MODULE = _selected
ACTIVE_ROLE = ROLE