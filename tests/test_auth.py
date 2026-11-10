"""Pruebas HTTP del módulo auth."""
import uuid

from tests.conftest import A, PASSWORD


def test_health_de_todos_los_modulos(client):
    assert client.get("/").status_code == 200
    for modulo in ("auth", "restaurants", "orders", "payments", "tracking"):
        assert client.get(f"{A}/{modulo}/health").status_code == 200


def test_registro_y_login(client):
    email = f"ana_{uuid.uuid4().hex[:8]}@test.com"
    datos = {"nombre_usuario": "ana", "email": email, "contrasenia": PASSWORD}

    r = client.post(f"{A}/auth/register", json=datos)
    assert r.status_code == 201
    assert "contrasenia" not in r.json()  # nunca se devuelve la contraseña

    assert client.post(f"{A}/auth/register", json=datos).status_code == 400  # email duplicado
    assert client.post(f"{A}/auth/register", json={**datos, "email": "x" + email, "contrasenia": "123"}).status_code == 400
    assert client.post(f"{A}/auth/register", json={**datos, "email": "no-es-email"}).status_code == 422

    r = client.post(f"{A}/auth/login", json={"email": email, "contrasenia": PASSWORD})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert client.post(f"{A}/auth/login", json={"email": email, "contrasenia": "incorrecta"}).status_code == 401

    assert client.get(f"{A}/auth/me", headers={"Authorization": f"Bearer {token}"}).json()["email"] == email
    assert client.get(f"{A}/auth/me").status_code == 401
    assert client.get(f"{A}/auth/me", headers={"Authorization": "Bearer token-falso"}).status_code == 401


def test_solo_admin_crea_admins(client, api):
    datos = {"nombre_usuario": "x", "email": f"adm_{uuid.uuid4().hex[:8]}@test.com", "contrasenia": PASSWORD, "rol_id": 3}
    assert client.post(f"{A}/auth/register", json=datos).status_code == 403
    assert client.post(f"{A}/auth/register", json=datos, headers=api.admin).status_code == 201


def test_permisos_sobre_usuarios(client, api):
    ana, beto = api.crear_usuario(), api.crear_usuario()
    assert client.get(f"{A}/auth/users", headers=ana["headers"]).status_code == 403
    assert client.get(f"{A}/auth/users", headers=api.admin).status_code == 200
    assert len(client.get(f"{A}/auth/users?limit=1", headers=api.admin).json()) == 1  # paginación
    assert client.get(f"{A}/auth/users/{beto['usuario_id']}", headers=ana["headers"]).status_code == 403
    assert client.get(f"{A}/auth/users/{ana['usuario_id']}", headers=ana["headers"]).status_code == 200
    assert client.get(f"{A}/auth/users/999999", headers=api.admin).status_code == 404


def test_suspender_usuario_bloquea_login(client, api):
    email = f"s_{uuid.uuid4().hex[:8]}@test.com"
    r = client.post(f"{A}/auth/register", json={"nombre_usuario": "s", "email": email, "contrasenia": PASSWORD})
    uid = r.json()["usuario_id"]

    assert client.patch(f"{A}/auth/users/{uid}/estado", json={"estado_id": 3}, headers=api.admin).status_code == 200
    assert client.post(f"{A}/auth/login", json={"email": email, "contrasenia": PASSWORD}).status_code == 400

    me = client.get(f"{A}/auth/me", headers=api.admin).json()
    assert client.patch(f"{A}/auth/users/{me['usuario_id']}/estado", json={"estado_id": 2}, headers=api.admin).status_code == 400


def test_contacto_y_direcciones(client, api):
    ana, beto = api.crear_usuario(), api.crear_cliente()
    h = ana["headers"]

    assert client.get(f"{A}/auth/me/contacto", headers=h).status_code == 404
    r = client.put(f"{A}/auth/me/contacto", json={"phone_personal": "70000000", "domicilio": "Calle 1"}, headers=h)
    assert r.status_code == 200
    r = client.put(f"{A}/auth/me/contacto", json={"phone_personal": "71111111"}, headers=h)  # actualiza
    assert r.json()["phone_personal"] == "71111111"

    r = client.post(f"{A}/auth/me/direcciones", json={"direccion_texto": "Av. 2", "etiqueta": "Trabajo"}, headers=h)
    assert r.status_code == 201
    direccion_id = r.json()["direccion_id"]
    assert client.post(f"{A}/auth/me/direcciones", json={"direccion_texto": "X", "latitud": 100}, headers=h).status_code == 422
    assert len(client.get(f"{A}/auth/me/direcciones", headers=h).json()) == 1

    # No puede borrar la dirección de otra persona
    assert client.delete(f"{A}/auth/me/direcciones/{beto['direccion_id']}", headers=h).status_code == 404
    assert client.delete(f"{A}/auth/me/direcciones/{direccion_id}", headers=h).status_code == 204
