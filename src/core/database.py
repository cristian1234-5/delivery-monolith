"""
Conexión central a la base de datos única del monolito.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from src.core.config import DATABASE_URL as _DATABASE_URL, DB_SCHEMA

# SQLAlchemy 2.1+ usa por defecto el driver "psycopg" (v3) para "postgresql://".
# El proyecto instala psycopg2-binary, así que se indica el driver explícitamente.
if _DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = _DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    DATABASE_URL = _DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    # init.sql crea las tablas dentro del esquema "delivery".
    # Con search_path, SQLAlchemy trabaja sobre ese esquema en cada conexión.
    connect_args = {"options": f"-csearch_path={DB_SCHEMA},public"}
elif DATABASE_URL.startswith("sqlite"):
    # SQLite solo se usa para las pruebas automáticas (tests/)
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _activar_foreign_keys(dbapi_conn, _):
        # SQLite no valida llaves foráneas por defecto (PostgreSQL sí)
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Una sesión = una transacción por petición HTTP (Unit of Work).
    Los repositorios solo hacen flush(); el servicio confirma con commit()
    al final del caso de uso. Si algo falla, se revierte TODO junto.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
