"""
Configuración central de la aplicación.
Lee las variables de entorno (docker-compose o archivo .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://delivery_user:delivery_password@localhost:5432/delivery_db",
)
# Esquema de PostgreSQL donde init.sql crea las tablas
DB_SCHEMA = os.getenv("DB_SCHEMA", "delivery")
APP_ENV = os.getenv("APP_ENV", "development")
