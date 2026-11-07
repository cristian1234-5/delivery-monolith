# modulo payment
''' Excepciones de negocio del módulo payment '''


class DomainException(Exception):
    """Excepción base de dominio (el router la traduce a HTTP 400)."""


class EntidadNoEncontradaException(DomainException):
    """Recurso no encontrado (el router la traduce a HTTP 404)."""


class PagoNoEncontradoException(EntidadNoEncontradaException):
    pass


class PedidoNoValidoParaPagoException(DomainException):
    pass


class PagoDuplicadoException(DomainException):
    pass


class MontoIncorrectoException(DomainException):
    pass


class PagoInvalidoException(DomainException):
    pass
