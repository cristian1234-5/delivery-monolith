# modulo payment
''' Casos de uso del módulo payment. '''
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual
from src.modules.payment.infraestructure.repository_impl import PaymentRepositorySqlAlchemy
from src.modules.payment.infraestructure.external_adapters import (
    PedidoAdapter,
    RepartidorAdapter,
    PasarelaPagoSimulada,
)
from src.modules.payment.domain.models import Pago
from src.modules.payment.domain.exceptions import (
    AccesoDenegadoException,
    PagoNoEncontradoException,
    PedidoNoValidoParaPagoException,
    PagoDuplicadoException,
    MontoIncorrectoException,
    PagoInvalidoException,
)
from src.modules.payment.presentation.schemas import PagoCreate


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PaymentRepositorySqlAlchemy(db)
        self.pedidos = PedidoAdapter(db)
        self.repartidores = RepartidorAdapter(db)
        self.pasarela = PasarelaPagoSimulada()

    # ============ Permisos ============
    def _obtener_pedido(self, pedido_id: int):
        pedido = self.pedidos.obtener_pedido(pedido_id)
        if not pedido:
            raise PedidoNoValidoParaPagoException(f"No existe el pedido con id {pedido_id}.")
        return pedido

    def _es_repartidor_del_pedido(self, pedido, actor: UsuarioActual) -> bool:
        return (
            actor.es_repartidor
            and pedido.repartidor_id is not None
            and pedido.repartidor_id == self.repartidores.repartidor_id_de_usuario(actor.usuario_id)
        )

    def _verificar_acceso(self, pedido, actor: UsuarioActual) -> None:
        if actor.es_admin or pedido.usuario_id == actor.usuario_id or self._es_repartidor_del_pedido(pedido, actor):
            return
        raise AccesoDenegadoException("No tiene acceso a los pagos de este pedido.")

    # ============ Casos de uso ============
    def procesar_pago(self, data: PagoCreate, actor: UsuarioActual) -> Pago:
        # 1. El pedido debe existir, ser del cliente y no estar cancelado (módulo order)
        pedido = self._obtener_pedido(data.pedido_id)
        if not actor.es_admin and pedido.usuario_id != actor.usuario_id:
            raise AccesoDenegadoException("Solo el cliente dueño del pedido puede pagarlo.")
        if pedido.estado == "Cancelado":
            raise PedidoNoValidoParaPagoException("No se puede pagar un pedido cancelado.")

        # 2. Un pedido tiene un único pago (se permite reintentar si el anterior falló)
        existente = self.repository.obtener_por_pedido(data.pedido_id)
        if existente and existente.estado_pago != "Fallido":
            raise PagoDuplicadoException(f"El pedido {data.pedido_id} ya tiene un pago registrado.")

        # 3. El monto debe coincidir con el total del pedido
        monto = Decimal(str(data.monto)).quantize(Decimal("0.01"))
        total = Decimal(str(pedido.sum_total)).quantize(Decimal("0.01"))
        if monto != total:
            raise MontoIncorrectoException(f"El monto {monto} no coincide con el total del pedido ({total}).")

        pago = Pago(
            pago_id=existente.pago_id if existente else None,
            pedido_id=data.pedido_id,
            monto=monto,
            metodo_pago=data.metodo_pago,
        )

        # 4. Efectivo queda Pendiente (se cobra al entregar); Tarjeta/QR pasan por la pasarela
        if not pago.es_contra_entrega():
            aprobado, transaccion_id = self.pasarela.cobrar(pago.monto, pago.metodo_pago)
            if aprobado:
                pago.completar(transaccion_id)
            else:
                pago.marcar_fallido(transaccion_id)

        pago = self.repository.guardar(pago)
        self.db.commit()
        return pago

    def confirmar_pago_efectivo(self, pago_id: int, actor: UsuarioActual) -> Pago:
        """El repartidor (o el admin) confirma que cobró en efectivo."""
        pago = self.repository.obtener_por_id(pago_id)
        if not pago:
            raise PagoNoEncontradoException(f"No existe el pago con id {pago_id}.")
        pedido = self._obtener_pedido(pago.pedido_id)
        if not actor.es_admin and not self._es_repartidor_del_pedido(pedido, actor):
            raise AccesoDenegadoException("Solo el repartidor asignado o un admin confirman el cobro.")
        if not pago.es_contra_entrega():
            raise PagoInvalidoException("Solo los pagos en efectivo se confirman manualmente.")
        if pedido.estado == "Cancelado":
            raise PagoInvalidoException("El pedido fue cancelado; no se puede confirmar el cobro.")

        pago.completar(self.pasarela.generar_comprobante_efectivo())
        pago = self.repository.guardar(pago)
        self.db.commit()
        return pago

    def obtener_pago(self, pago_id: int, actor: UsuarioActual) -> Pago:
        pago = self.repository.obtener_por_id(pago_id)
        if not pago:
            raise PagoNoEncontradoException(f"No existe el pago con id {pago_id}.")
        self._verificar_acceso(self._obtener_pedido(pago.pedido_id), actor)
        return pago

    def obtener_pago_de_pedido(self, pedido_id: int, actor: UsuarioActual) -> Pago:
        self._verificar_acceso(self._obtener_pedido(pedido_id), actor)
        pago = self.repository.obtener_por_pedido(pedido_id)
        if not pago:
            raise PagoNoEncontradoException(f"El pedido {pedido_id} no tiene pagos registrados.")
        return pago

    def listar_pagos(self, skip: int = 0, limit: int = 50) -> List[Pago]:
        return self.repository.listar_todos(skip, limit)
