# modulo restaurant
''' Entidades puras de dominio
========================================
Restaurante y Producto con sus reglas de negocio, sin depender de SQLAlchemy.
'''
from dataclasses import dataclass
from datetime import time
from decimal import Decimal
from typing import Optional

from src.modules.restaurant.domain.exceptions import (
    DatosRestauranteInvalidosException,
    DatosProductoInvalidosException,
)

ESTADOS_RESTAURANTE = ("Abierto", "Cerrado")


@dataclass
class Restaurante:
    nombre: str
    direccion: str
    contacto: Optional[str] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: str = "Abierto"
    restaurant_id: Optional[int] = None

    def __post_init__(self):
        self.validar()

    def validar(self):
        if not self.nombre or not self.nombre.strip():
            raise DatosRestauranteInvalidosException("El nombre del restaurante es obligatorio.")
        if not self.direccion or not self.direccion.strip():
            raise DatosRestauranteInvalidosException("La dirección del restaurante es obligatoria.")
        if self.estado not in ESTADOS_RESTAURANTE:
            raise DatosRestauranteInvalidosException(f"Estado inválido. Use: {', '.join(ESTADOS_RESTAURANTE)}.")
        if self.horario_apertura and self.horario_cierre and self.horario_apertura == self.horario_cierre:
            raise DatosRestauranteInvalidosException("El horario de apertura y cierre no pueden ser iguales.")

    def abrir(self):
        self.estado = "Abierto"

    def cerrar(self):
        self.estado = "Cerrado"

    def esta_abierto(self) -> bool:
        return self.estado == "Abierto"

    def esta_en_horario(self, hora: time) -> bool:
        """Regla de negocio: ¿la hora indicada está dentro del horario de atención?"""
        if not self.horario_apertura or not self.horario_cierre:
            return True  # Sin horario definido = atiende todo el día
        if self.horario_apertura < self.horario_cierre:
            return self.horario_apertura <= hora < self.horario_cierre
        # Horario que cruza la medianoche (ej. 18:00 a 02:00)
        return hora >= self.horario_apertura or hora < self.horario_cierre


@dataclass
class Producto:
    nombre: str
    precio: Decimal
    categoria: str
    restaurant_id: int
    descripcion: Optional[str] = None
    disponible: bool = True
    producto_id: Optional[int] = None

    def __post_init__(self):
        self.precio = Decimal(str(self.precio))
        self.validar()

    def validar(self):
        if not self.nombre or not self.nombre.strip():
            raise DatosProductoInvalidosException("El nombre del producto es obligatorio.")
        if not self.categoria or not self.categoria.strip():
            raise DatosProductoInvalidosException("La categoría del producto es obligatoria.")
        if self.precio < 0:
            raise DatosProductoInvalidosException("El precio no puede ser negativo.")

    def cambiar_precio(self, nuevo_precio: Decimal):
        self.precio = Decimal(str(nuevo_precio))
        self.validar()

    def puede_venderse(self) -> bool:
        return self.disponible
