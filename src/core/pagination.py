"""
Parámetros de paginación reutilizables: ?skip=0&limit=50
"""
from fastapi import Query


class Paginacion:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
        limit: int = Query(50, ge=1, le=200, description="Máximo de registros a devolver"),
    ):
        self.skip = skip
        self.limit = limit
