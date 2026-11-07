# modulo auth
''' Excepciones de negocio del módulo auth '''


class DomainException(Exception):
    """Excepción base de dominio (el router la traduce a HTTP 400)."""


class EntidadNoEncontradaException(DomainException):
    """Recurso no encontrado (el router la traduce a HTTP 404)."""


class EmailYaRegistradoException(DomainException):
    pass


class UsuarioNoEncontradoException(EntidadNoEncontradaException):
    pass


class CredencialesInvalidasException(DomainException):
    pass


class UsuarioInactivoException(DomainException):
    pass
