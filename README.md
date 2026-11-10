# Delivery Platform — Monolito Modular (DDD)

API de una plataforma de delivery construida como **monolito modular** con **FastAPI**,
**SQLAlchemy** y **PostgreSQL**, organizada por dominios según **Domain-Driven Design**.

## Arquitectura

Una sola aplicación y una sola base de datos, divididas en 5 módulos independientes:

| Módulo | Responsabilidad |
|---|---|
| `auth` | Usuarios, login con JWT, roles, contacto y direcciones |
| `restaurant` | Restaurantes, horarios y menú de productos |
| `order` | Pedidos, detalle y ciclo de vida del pedido |
| `payment` | Pagos (efectivo, tarjeta, QR) |
| `tracking` | Repartidores, ubicación GPS y seguimiento del pedido |

Cada módulo tiene las mismas 4 capas:

```
src/modules/<modulo>/
├── domain/
│   ├── models.py            Entidades puras (@dataclass) con las reglas de negocio
│   ├── exceptions.py        Errores de negocio
│   └── repositories.py      Contrato abstracto (ABC)
├── application/
│   ├── services.py          Casos de uso (orquestan dominio + repositorio)
│   └── dtos.py
├── infraestructure/         (en auth: infrastructure/)
│   ├── models_db.py         Modelos ORM de SQLAlchemy (tablas)
│   ├── repository_impl.py   Implementación del contrato con SQLAlchemy + mapeador
│   └── external_adapters.py Cómo este módulo consulta a OTROS módulos
└── presentation/
    ├── schemas.py           DTOs de Pydantic (entrada/salida HTTP)
    └── router.py            Endpoints de FastAPI
```

`src/core/` es el núcleo compartido: configuración, conexión a la BD, seguridad JWT,
paginación y reloj.

**Reglas de diseño**

- Un módulo **nunca** consulta las tablas de otro: lo hace por su `external_adapters.py`.
  Si un módulo se separa después en un microservicio, solo se reescribe ese adaptador.
- **Una transacción por caso de uso:** los repositorios solo hacen `flush()` y el servicio
  hace un único `commit()`. Por ejemplo, al asignar un repartidor se guardan juntos el
  pedido y la disponibilidad del repartidor. Si algo falla, no se guarda nada.
- Las reglas de negocio viven en las entidades de dominio y se prueban sin base de datos
  (`tests/test_dominio.py`).

## Cómo ejecutarlo

Necesita **Docker Desktop**.

```bash
docker compose up --build
```

- API: http://localhost:8000
- Documentación interactiva (Swagger): http://localhost:8000/docs

> Si ya había levantado una versión anterior, borre el volumen para que `init.sql` se
> vuelva a ejecutar: `docker compose down -v` y luego `docker compose up --build`.

### Administrador inicial

Al arrancar se crea un admin si no existe ninguno (se configura en `docker-compose.yml`):

- Email: `admin@delivery.com`
- Contraseña: `admin123`

**Cambie `ADMIN_PASSWORD` y `SECRET_KEY` antes de usarlo fuera de clase.**

### Autenticarse en Swagger

1. `POST /api/v1/auth/login` con email y contraseña.
2. Copie el `access_token` de la respuesta.
3. Presione **Authorize** (arriba a la derecha), pegue el token y confirme.

## Roles y permisos

| Acción | Cliente | Repartidor | Admin |
|---|:-:|:-:|:-:|
| Ver restaurantes y menú (sin login) | ✔ | ✔ | ✔ |
| Crear/editar restaurantes y productos | | | ✔ |
| Registrar sus direcciones y contacto | ✔ | ✔ | ✔ |
| Crear un pedido | ✔ | | |
| Ver un pedido | el suyo | si lo tiene asignado | todos |
| Cancelar un pedido (solo si está Pendiente) | el suyo | | ✔ |
| Pasar a `En_Preparacion` | | | ✔ |
| Pasar a `En_Camino` / `Entregado` | | si lo tiene asignado | ✔ |
| Asignar repartidor | | | ✔ |
| Pagar un pedido | el suyo | | ✔ |
| Confirmar cobro en efectivo | | si lo tiene asignado | ✔ |
| Reportar ubicación GPS | | la suya | |
| Ver seguimiento del pedido | el suyo | si lo tiene asignado | ✔ |
| Listar usuarios, pedidos, pagos y repartidores | | | ✔ |
| Suspender/activar usuarios | | | ✔ |

## Reglas de negocio principales

- **Usuarios:** contraseña de al menos 6 caracteres, guardada con hash PBKDF2. Solo un admin
  crea otros admins. Un usuario suspendido no puede iniciar sesión ni hacer pedidos.
- **Restaurantes:** solo reciben pedidos si están `Abierto` y dentro de su horario (se
  admiten horarios que cruzan la medianoche, por ejemplo de 18:00 a 02:00). La zona horaria
  es `America/La_Paz`.
- **Pedidos:** deben tener al menos un producto y una dirección de entrega del propio cliente.
  Los productos tienen que ser del restaurante y estar disponibles, y **el precio sale del
  catálogo**, nunca del cliente. Flujo de estados:
  `Pendiente → En_Preparacion → En_Camino → Entregado`. Solo se puede cancelar mientras está
  Pendiente, y para pasar a En_Camino debe tener un repartidor asignado.
- **Repartidores:** si van en Moto o Taxi deben tener placa. Al asignarles un pedido quedan
  ocupados, y al entregarlo o cancelarlo vuelven a quedar libres.
- **Pagos:** un pago por pedido, y el monto debe ser igual al total. Tarjeta y QR pasan por
  una pasarela simulada. El efectivo queda `Pendiente` y se marca `Completado` solo cuando se
  entrega el pedido (o cuando lo confirma el repartidor). No se pagan pedidos cancelados.
- **Errores de base de datos:** por ejemplo, borrar un restaurante que tiene pedidos. La API
  responde **409** con un mensaje claro, en lugar de un error 500. Para retirar un producto
  que ya se vendió, márquelo como `disponible: false`.

## Flujo de ejemplo

1. **Admin:** `POST /restaurants/` y `POST /restaurants/{id}/productos`.
2. **Cliente:** `POST /auth/register`, luego `POST /auth/login` y luego `POST /auth/me/direcciones`.
3. **Cliente:** `POST /orders/` con `restaurant_id`, `direccion_id` e `items`.
4. **Cliente:** `POST /payments/` con el `sum_total` del pedido.
5. **Admin:** registra al repartidor (`POST /auth/register` con `rol_id: 2` y después
   `POST /tracking/repartidores`), pasa el pedido a `En_Preparacion` y lo asigna con
   `PATCH /orders/{id}/repartidor`.
6. **Repartidor:** `PATCH /orders/{id}/estado` a `En_Camino`, va enviando
   `POST /tracking/repartidores/{id}/ubicaciones` y al final marca `Entregado`.
7. **Cliente:** sigue su pedido con `GET /tracking/pedido/{id}`.

Todas las rutas empiezan con `/api/v1`. Los listados aceptan paginación con `?skip=0&limit=50`.

## Pruebas automáticas

```bash
pip install -r requirements-dev.txt
pytest
```

- `tests/test_dominio.py`: reglas de negocio puras, sin base de datos.
- `tests/test_<modulo>.py`: endpoints, permisos y la integración entre módulos.

Por defecto las pruebas usan SQLite temporal, así que no necesitan Docker. Para correrlas
contra PostgreSQL, defina `TEST_DATABASE_URL` con una base vacía en la que ya se haya
ejecutado `init.sql`.

## Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `DATABASE_URL` | `postgresql://delivery_user:...@localhost:5432/delivery_db` | Conexión a la BD |
| `DB_SCHEMA` | `delivery` | Esquema de PostgreSQL |
| `SECRET_KEY` | `cambiar-esta-clave-en-produccion` | Firma de los tokens JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Duración del token |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `admin@delivery.com` / `admin123` | Admin inicial |
| `APP_TIMEZONE` | `America/La_Paz` | Zona horaria de los horarios |
| `CORS_ORIGINS` | `*` | Frontends permitidos (separados por coma) |
