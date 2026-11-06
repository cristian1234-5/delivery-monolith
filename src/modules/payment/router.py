from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_payment_status():
    return {
        "module": "payment",
        "status": "active"
    }


@router.post("/")
def process_payment(payment_data: dict):
    return {
        "message": "Pago procesado exitosamente",
        "payment_id": "PAY-12345",
        "status": "APPROVED"
    }


