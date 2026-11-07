# modulo restaurant
''' Excepciones de negocio del módulo restaurant '''


class DomainException(Exception):
    """Excepción base de dominio (el router la traduce a HTTP 400)."""


class EntidadNoEncontradaException(DomainException):
    """Recurso no encontrado (el router la traduce a HTTP 404)."""


class RestauranteNoEncontradoException(EntidadNoEncontradaException):
    pass


class ProductoNoEncontradoException(EntidadNoEncontradaException):
    pass


class DatosRestauranteInvalidosException(DomainException):
    pass


class DatosProductoInvalidosException(DomainException):
    pass
