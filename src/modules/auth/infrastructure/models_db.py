# modulo auth
''' Modelos ORM de SQLAlchemy
========================================
Modelos ORM de las tablas rol, estado, usuario, contacto y direccion.
'''

from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class RolModel(Base):
    __tablename__ = "rol"

    rol_id = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), nullable=False, unique=True)


class EstadoModel(Base):
    __tablename__ = "estado"

    estado_id = Column(Integer, primary_key=True, index=True)
    nombre_estado = Column(String(50), nullable=False, unique=True)


class UsuarioModel(Base):
    __tablename__ = "usuario"

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(64), nullable=False)
    contrasenia = Column(String(255), nullable=False)
    email = Column(String(128), nullable=False, unique=True)

    rol_id = Column(Integer, ForeignKey("rol.rol_id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estado.estado_id"), nullable=False)

    # Relaciones ORM
    rol = relationship("RolModel")
    estado = relationship("EstadoModel")
    contacto = relationship(
        "ContactoModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    direcciones = relationship(
        "DireccionModel", back_populates="usuario", cascade="all, delete-orphan"
    )


class ContactoModel(Base):
    __tablename__ = "contacto"

    contacto_id = Column(Integer, primary_key=True, index=True)
    phone_personal = Column(String(20))
    phone_trabajo = Column(String(20))
    domicilio = Column(String(255))

    usuario_id = Column(
        Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False, unique=True
    )

    usuario = relationship("UsuarioModel", back_populates="contacto")


class DireccionModel(Base):
    __tablename__ = "direccion"

    direccion_id = Column(Integer, primary_key=True, index=True)
    direccion_texto = Column(String(255), nullable=False)
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    referencia = Column(String(255))
    etiqueta = Column(String(50))
    es_temporal = Column(Boolean, default=False)

    usuario_id = Column(
        Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False
    )

    usuario = relationship("UsuarioModel", back_populates="direcciones")
