"""
Configuración central de la aplicación.
Lee las variables de entorno (docker-compose o archivo .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- Base de datos ----------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://delivery_user:delivery_password@localhost:5432/delivery_db",
)
# Esquema de PostgreSQL donde init.sql crea las tablas
DB_SCHEMA = os.getenv("DB_SCHEMA", "delivery")
APP_ENV = os.getenv("APP_ENV", "development")

# ---------- Seguridad (JWT) ----------
# IMPORTANTE: en producción cambie SECRET_KEY por un valor largo y aleatorio.
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# Usuario administrador que se crea al iniciar si no existe ninguno
ADMIN_NOMBRE = os.getenv("ADMIN_NOMBRE", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@delivery.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ---------- Varios ----------
# Zona horaria para validar el horario de los restaurantes
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "America/La_Paz")
# Orígenes permitidos para CORS (frontend), separados por coma. "*" = todos
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
