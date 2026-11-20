"""
Configuración de las pruebas.
- Por defecto usan una base SQLite temporal (no necesitan Docker).
- Para probar contra PostgreSQL: defina TEST_DATABASE_URL antes de correr pytest
  (la base debe estar vacía y con init.sql ya ejecutado).
"""
import os
import tempfile
import uuid

_url = os.environ.get("TEST_DATABASE_URL")
if not _url:
    _url = f"sqlite:///{os.path.join(tempfile.mkdtemp(), 'test.db')}"
os.environ["DATABASE_URL"] = _url
os.environ["ADMIN_EMAIL"] = "admin@delivery.com"
os.environ["ADMIN_PASSWORD"] = "admin123"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402

A = "/api/v1"
PASSWORD = "secreto123"


class Api:
    """Atajos para preparar datos en las pruebas."""

    def __init__(self, client: TestClient):
        self.c = client
        self.admin = self.login("admin@delivery.com", "admin123")

    def login(self, email: str, contrasenia: str) -> dict:
        r = self.c.post(f"{A}/auth/login", json={"email": email, "contrasenia": contrasenia})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    def crear_usuario(self, rol_id: int = 1) -> dict:
        email = f"u_{uuid.uuid4().hex[:10]}@test.com"
        r = self.c.post(
            f"{A}/auth/register",
            json={"nombre_usuario": "usuario", "email": email, "contrasenia": PASSWORD, "rol_id": rol_id},
            headers=self.admin,
        )
        assert r.status_code == 201, r.text
        usuario = r.json()
        usuario["headers"] = self.login(email, PASSWORD)
        return usuario

    def crear_cliente(self) -> dict:
        cliente = self.crear_usuario(rol_id=1)
        r = self.c.post(
            f"{A}/auth/me/direcciones",
            json={"direccion_texto": "Calle 1 #123", "latitud": -17.78, "longitud": -63.18, "etiqueta": "Casa"},
            headers=cliente["headers"],
        )
        assert r.status_code == 201, r.text
        cliente["direccion_id"] = r.json()["direccion_id"]
        return cliente

    def crear_repartidor(self) -> dict:
        repartidor = self.crear_usuario(rol_id=2)
        r = self.c.post(
            f"{A}/tracking/repartidores",
            json={"tipo_vehiculo": "Moto", "placa": "1234ABC", "usuario_id": repartidor["usuario_id"]},
            headers=self.admin,
        )
        assert r.status_code == 201, r.text
        repartidor["repartidor_id"] = r.json()["repartidor_id"]
        return repartidor

    def crear_restaurante(self, **extra) -> int:
        datos = {"nombre": "Burger House", "direccion": "Av. Principal", **extra}
        r = self.c.post(f"{A}/restaurants/", json=datos, headers=self.admin)
        assert r.status_code == 201, r.text
        return r.json()["restaurant_id"]

    def crear_producto(self, restaurant_id: int, precio: float = 10, disponible: bool = True) -> int:
        r = self.c.post(
            f"{A}/restaurants/{restaurant_id}/productos",
            json={"nombre": "Producto", "precio": precio, "categoria": "Comida", "disponible": disponible},
            headers=self.admin,
        )
        assert r.status_code == 201, r.text
        return r.json()["producto_id"]

    def crear_pedido(self, cliente: dict, restaurant_id: int, items: list) -> dict:
        r = self.c.post(
            f"{A}/orders/",
            json={"restaurant_id": restaurant_id, "direccion_id": cliente["direccion_id"], "items": items},
            headers=cliente["headers"],
        )
        assert r.status_code == 201, r.text
        return r.json()

    def asignar(self, pedido_id: int, repartidor: dict):
        r = self.c.patch(
            f"{A}/orders/{pedido_id}/repartidor",
            json={"repartidor_id": repartidor["repartidor_id"]},
            headers=self.admin,
        )
        assert r.status_code == 200, r.text
        return r.json()

    def estado(self, pedido_id: int, estado: str, headers: dict):
        return self.c.patch(f"{A}/orders/{pedido_id}/estado", json={"estado": estado}, headers=headers)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # "with" ejecuta el arranque (crea admin y catálogos)
        yield c


@pytest.fixture(scope="session")
def api(client):
    return Api(client)
