# modulo tracking
''' Excepciones de negocio del módulo tracking '''


class DomainException(Exception):
    """Excepción base de dominio (el router la traduce a HTTP 400)."""


class EntidadNoEncontradaException(DomainException):
    """Recurso no encontrado (el router la traduce a HTTP 404)."""


class AccesoDenegadoException(DomainException):
    """El usuario no puede ver o modificar este recurso (HTTP 403)."""


class RepartidorNoEncontradoException(EntidadNoEncontradaException):
    pass


class PedidoNoEncontradoException(EntidadNoEncontradaException):
    pass


class SinUbicacionException(EntidadNoEncontradaException):
    pass


class DatosRepartidorInvalidosException(DomainException):
    pass


class UbicacionInvalidaException(DomainException):
    pass


class UsuarioNoValidoException(DomainException):
    pass
