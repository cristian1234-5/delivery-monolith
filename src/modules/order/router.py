from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db

router = APIRouter()

@router.post("/")
def create_order(order_data: dict, db: Session = Depends(get_db)):
    # Lógica aislada del Módulo de Pedidos
    return {"message": "Pedido creado exitosamente", "order_id": "ORD-12345", "status": "PENDING"}

@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    return {"order_id": order_id, "status": "IN_PREPARATION", "items": ["Hamburguesa", "Papas"]}

