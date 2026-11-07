# modulo order
''' Excepciones de negocio del módulo order '''


class DomainException(Exception):
    """Excepción base de dominio (el router la traduce a HTTP 400)."""


class EntidadNoEncontradaException(DomainException):
    """Recurso no encontrado (el router la traduce a HTTP 404)."""


class PedidoNoEncontradoException(EntidadNoEncontradaException):
    pass


class UsuarioNoValidoException(DomainException):
    pass


class RestauranteNoDisponibleException(DomainException):
    pass


class ProductoNoValidoException(DomainException):
    pass


class RepartidorNoDisponibleException(DomainException):
    pass


class PedidoInvalidoException(DomainException):
    pass


class TransicionEstadoInvalidaException(DomainException):
    pass


class CancelacionNoPermitidaException(DomainException):
    pass
