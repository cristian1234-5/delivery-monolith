# modulo tracking
''' Adaptadores externos del módulo tracking.
========================================
- UsuarioAdapter: valida en el módulo auth que el usuario exista y tenga rol repartidor.
- PedidoAdapter: consulta el módulo order para el seguimiento de un pedido.
'''
from sqlalchemy.orm import Session

from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.order.infraestructure.repository_impl import OrderRepositorySqlAlchemy

ROL_REPARTIDOR_ID = 2  # 'repartidor' en la tabla rol (init.sql)


class UsuarioAdapter:
    """Consulta el módulo auth."""

    def __init__(self, db: Session):
        self._repo = AuthRepositorySqlAlchemy(db)

    def obtener_usuario(self, usuario_id: int):
        return self._repo.obtener_por_id(usuario_id)

    def es_repartidor(self, usuario_id: int) -> bool:
        usuario = self._repo.obtener_por_id(usuario_id)
        return usuario is not None and usuario.rol_id == ROL_REPARTIDOR_ID


class PedidoAdapter:
    """Consulta el módulo order."""

    def __init__(self, db: Session):
        self._repo = OrderRepositorySqlAlchemy(db)

    def obtener_pedido(self, pedido_id: int):
        return self._repo.obtener_por_id(pedido_id)
