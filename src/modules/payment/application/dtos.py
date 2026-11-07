# modulo payment
''' DTOs de la capa de aplicación.
Los DTOs HTTP (entrada/salida) se definen en presentation/schemas.py y se reutilizan aquí.
'''
from src.modules.payment.presentation.schemas import PagoCreate, PagoResponse

__all__ = ["PagoCreate", "PagoResponse"]
