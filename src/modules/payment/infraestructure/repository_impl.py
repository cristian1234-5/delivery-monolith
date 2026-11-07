# modulo payment
''' Implementación concreta del repositorio con SQLAlchemy.
Traduce PagoModel (BD) <-> Pago (dominio).
'''
from typing import Optional, List
from sqlalchemy.orm import Session

from src.modules.payment.domain.repositories import IPaymentRepository
from src.modules.payment.domain.models import Pago
from src.modules.payment.infraestructure.models_db import PagoModel


class PaymentRepositorySqlAlchemy(IPaymentRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: PagoModel) -> Optional[Pago]:
        if not model:
            return None
        return Pago(
            pago_id=model.pago_id,
            pedido_id=model.pedido_id,
            monto=model.monto,
            metodo_pago=model.metodo_pago,
            estado_pago=model.estado_pago,
            transaccion_id=model.transaccion_id,
            fecha=model.fecha,
        )

    def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
        model = self.db.query(PagoModel).filter(PagoModel.pago_id == pago_id).first()
        return self._to_domain(model)

    def obtener_por_pedido(self, pedido_id: int) -> Optional[Pago]:
        model = self.db.query(PagoModel).filter(PagoModel.pedido_id == pedido_id).first()
        return self._to_domain(model)

    def listar_todos(self) -> List[Pago]:
        return [self._to_domain(m) for m in self.db.query(PagoModel).order_by(PagoModel.pago_id.desc()).all()]

    def guardar(self, pago: Pago) -> Pago:
        model = None
        if pago.pago_id:
            model = self.db.query(PagoModel).filter(PagoModel.pago_id == pago.pago_id).first()
        if not model:
            model = PagoModel(pedido_id=pago.pedido_id)
            self.db.add(model)

        model.monto = pago.monto
        model.metodo_pago = pago.metodo_pago
        model.estado_pago = pago.estado_pago
        model.transaccion_id = pago.transaccion_id
        model.fecha = pago.fecha

        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)
