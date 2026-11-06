from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_tracking_status():
    return {
        "module": "tracking",
        "status": "active"
    }


@router.get("/{order_id}")
def track_order(order_id: str):
    return {
        "order_id": order_id,
        "status": "IN_DELIVERY",
        "location": "Centro de distribución"
    }
