# modulo payment
''' Casos de uso del módulo payment. '''
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session

from src.modules.payment.infraestructure.repository_impl import PaymentRepositorySqlAlchemy
from src.modules.payment.infraestructure.external_adapters import PedidoAdapter, PasarelaPagoSimulada
from src.modules.payment.domain.models import Pago
from src.modules.payment.domain.exceptions import (
    PagoNoEncontradoException,
    PedidoNoValidoParaPagoException,
    PagoDuplicadoException,
    MontoIncorrectoException,
    PagoInvalidoException,
)
from src.modules.payment.presentation.schemas import PagoCreate


class PaymentService:
    def __init__(self, db: Session):
        self.repository = PaymentRepositorySqlAlchemy(db)
        self.pedidos = PedidoAdapter(db)
        self.pasarela = PasarelaPagoSimulada()

    def procesar_pago(self, data: PagoCreate) -> Pago:
        # 1. El pedido debe existir y no estar cancelado (módulo order)
        pedido = self.pedidos.obtener_pedido(data.pedido_id)
        if not pedido:
            raise PedidoNoValidoParaPagoException(f"No existe el pedido con id {data.pedido_id}.")
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

        return self.repository.guardar(pago)

    def confirmar_pago_efectivo(self, pago_id: int) -> Pago:
        pago = self.obtener_pago(pago_id)
        if not pago.es_contra_entrega():
            raise PagoInvalidoException("Solo los pagos en efectivo se confirman manualmente.")
        pago.completar(self.pasarela.generar_comprobante_efectivo())
        return self.repository.guardar(pago)

    def obtener_pago(self, pago_id: int) -> Pago:
        pago = self.repository.obtener_por_id(pago_id)
        if not pago:
            raise PagoNoEncontradoException(f"No existe el pago con id {pago_id}.")
        return pago

    def obtener_pago_de_pedido(self, pedido_id: int) -> Pago:
        pago = self.repository.obtener_por_pedido(pedido_id)
        if not pago:
            raise PagoNoEncontradoException(f"El pedido {pedido_id} no tiene pagos registrados.")
        return pago

    def listar_pagos(self) -> List[Pago]:
        return self.repository.listar_todos()
