from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_restaurants():
    return {
        "module": "restaurant",
        "status": "active",
        "restaurants": [
            {
                "id": 1,
                "name": "Burger House"
            },
            {
                "id": 2,
                "name": "Pizza Express"
            }
        ]
    }


@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    return {
        "restaurant_id": restaurant_id,
        "name": "Burger House",
        "status": "OPEN"
    }
