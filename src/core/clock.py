"""
Reloj de la aplicación en la zona horaria configurada (APP_TIMEZONE).
El contenedor Docker corre en UTC; los horarios de los restaurantes
se validan con la hora local.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.config import APP_TIMEZONE

_ZONA = ZoneInfo(APP_TIMEZONE)


def ahora_local() -> datetime:
    return datetime.now(_ZONA)
