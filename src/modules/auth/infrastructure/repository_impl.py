# modulo auth
''' Implementación concreta del repositorio con SQLAlchemy.
Traduce los modelos ORM (BD) <-> entidades de dominio.
Solo hace flush(): el commit lo decide el servicio (una transacción por caso de uso).
'''
from typing import Optional, List
from sqlalchemy.orm import Session

from src.core.security import ROL_ADMIN
from src.modules.auth.domain.repositories import IAuthRepository
from src.modules.auth.domain.models import Usuario, Contacto, Direccion
from src.modules.auth.infrastructure.models_db import (
    UsuarioModel,
    RolModel,
    EstadoModel,
    ContactoModel,
    DireccionModel,
)

ROLES_BASE = ("cliente", "repartidor", "admin")
ESTADOS_BASE = ("activo", "inactivo", "suspendido", "eliminado")


class AuthRepositorySqlAlchemy(IAuthRepository):
    def __init__(self, db: Session):
        self.db = db

    # ============ Mapeadores ============
    def _to_domain(self, model: UsuarioModel) -> Optional[Usuario]:
        """Convierte un modelo ORM de BD a una Entidad Pura de Dominio."""
        if not model:
            return None
        return Usuario(
            usuario_id=model.usuario_id,
            nombre_usuario=model.nombre_usuario,
            email=model.email,
            contrasenia=model.contrasenia,
            rol_id=model.rol_id,
            estado_id=model.estado_id,
        )

    def _contacto_to_domain(self, model: ContactoModel) -> Optional[Contacto]:
        if not model:
            return None
        return Contacto(
            contacto_id=model.contacto_id,
            usuario_id=model.usuario_id,
            phone_personal=model.phone_personal,
            phone_trabajo=model.phone_trabajo,
            domicilio=model.domicilio,
        )

    def _direccion_to_domain(self, model: DireccionModel) -> Optional[Direccion]:
        if not model:
            return None
        return Direccion(
            direccion_id=model.direccion_id,
            usuario_id=model.usuario_id,
            direccion_texto=model.direccion_texto,
            latitud=float(model.latitud) if model.latitud is not None else None,
            longitud=float(model.longitud) if model.longitud is not None else None,
            referencia=model.referencia,
            etiqueta=model.etiqueta,
            es_temporal=model.es_temporal,
        )

    # ============ Usuarios ============
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        db_model = self.db.query(UsuarioModel).filter(UsuarioModel.usuario_id == usuario_id).first()
        return self._to_domain(db_model)

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        db_model = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        return self._to_domain(db_model)

    def guardar(self, usuario: Usuario) -> Usuario:
        # Si ya tiene ID, actualizamos; si no, creamos el modelo de BD
        db_model = None
        if usuario.usuario_id:
            db_model = self.db.query(UsuarioModel).filter(UsuarioModel.usuario_id == usuario.usuario_id).first()
        if not db_model:
            db_model = UsuarioModel()
            self.db.add(db_model)

        db_model.nombre_usuario = usuario.nombre_usuario
        db_model.email = usuario.email
        db_model.contrasenia = usuario.contrasenia
        db_model.rol_id = usuario.rol_id
        db_model.estado_id = usuario.estado_id

        self.db.flush()
        self.db.refresh(db_model)
        return self._to_domain(db_model)

    def listar_todos(self, skip: int = 0, limit: int = 50) -> List[Usuario]:
        query = self.db.query(UsuarioModel).order_by(UsuarioModel.usuario_id).offset(skip).limit(limit)
        return [self._to_domain(m) for m in query.all()]

    def existe_admin(self) -> bool:
        return self.db.query(UsuarioModel).filter(UsuarioModel.rol_id == ROL_ADMIN).first() is not None

    def asegurar_catalogos(self) -> None:
        # En PostgreSQL init.sql ya los inserta; esto cubre otras BD (pruebas)
        for nombre in ROLES_BASE:
            if not self.db.query(RolModel).filter(RolModel.nombre_rol == nombre).first():
                self.db.add(RolModel(nombre_rol=nombre))
        for nombre in ESTADOS_BASE:
            if not self.db.query(EstadoModel).filter(EstadoModel.nombre_estado == nombre).first():
                self.db.add(EstadoModel(nombre_estado=nombre))
        self.db.flush()

    # ============ Contacto ============
    def obtener_contacto(self, usuario_id: int) -> Optional[Contacto]:
        model = self.db.query(ContactoModel).filter(ContactoModel.usuario_id == usuario_id).first()
        return self._contacto_to_domain(model)

    def guardar_contacto(self, contacto: Contacto) -> Contacto:
        model = self.db.query(ContactoModel).filter(ContactoModel.usuario_id == contacto.usuario_id).first()
        if not model:
            model = ContactoModel(usuario_id=contacto.usuario_id)
            self.db.add(model)
        model.phone_personal = contacto.phone_personal
        model.phone_trabajo = contacto.phone_trabajo
        model.domicilio = contacto.domicilio
        self.db.flush()
        self.db.refresh(model)
        return self._contacto_to_domain(model)

    # ============ Direcciones ============
    def listar_direcciones(self, usuario_id: int) -> List[Direccion]:
        query = (
            self.db.query(DireccionModel)
            .filter(DireccionModel.usuario_id == usuario_id)
            .order_by(DireccionModel.direccion_id)
        )
        return [self._direccion_to_domain(m) for m in query.all()]

    def obtener_direccion(self, direccion_id: int) -> Optional[Direccion]:
        model = self.db.query(DireccionModel).filter(DireccionModel.direccion_id == direccion_id).first()
        return self._direccion_to_domain(model)

    def guardar_direccion(self, direccion: Direccion) -> Direccion:
        model = None
        if direccion.direccion_id:
            model = self.db.query(DireccionModel).filter(
                DireccionModel.direccion_id == direccion.direccion_id
            ).first()
        if not model:
            model = DireccionModel(usuario_id=direccion.usuario_id)
            self.db.add(model)
        model.direccion_texto = direccion.direccion_texto
        model.latitud = direccion.latitud
        model.longitud = direccion.longitud
        model.referencia = direccion.referencia
        model.etiqueta = direccion.etiqueta
        model.es_temporal = direccion.es_temporal
        self.db.flush()
        self.db.refresh(model)
        return self._direccion_to_domain(model)

    def eliminar_direccion(self, direccion_id: int) -> None:
        model = self.db.query(DireccionModel).filter(DireccionModel.direccion_id == direccion_id).first()
        if model:
            self.db.delete(model)
            self.db.flush()
