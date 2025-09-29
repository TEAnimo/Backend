from sqlalchemy import (
    Column, Integer, SmallInteger, Text, String, Numeric, Boolean, CHAR, DateTime,
    UniqueConstraint, Index, text, func
)
from datetime import datetime, timezone
from sqlalchemy.orm import validates
from passlib.context import CryptContext
from .database import Base

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    edad = Column(SmallInteger)
    sexo = Column(CHAR(1))

    a1 = Column(SmallInteger)
    a2 = Column(SmallInteger)
    a3 = Column(SmallInteger)
    a4 = Column(SmallInteger)
    a5 = Column(SmallInteger)
    a6 = Column(SmallInteger)
    a7 = Column(SmallInteger)
    a8 = Column(SmallInteger)
    a9 = Column(SmallInteger)
    a10 = Column(SmallInteger)

    qchat_resultado = Column(SmallInteger)

    trastorno_habla = Column(String(2))
    trastorno_aprendizaje = Column(String(2))
    trastorno_genetico = Column(String(2))
    trastorno_depresion = Column(String(2))
    retraso_global_intelectual = Column(String(2))
    problemas_comportamiento = Column(String(2))
    trastorno_ansiedad = Column(String(2))
    familiar_autista = Column(String(2))

    porc_comorbilidad = Column(Numeric(3, 2))
    porc_deficiencia_social_interactiva = Column(Numeric(3, 2))
    porc_deficiencia_comunicativa = Column(Numeric(3, 2))

    perfil_clinico = Column(String(30))

    rasgos_tea = Column(String(2))  # 'Si' o 'No'
    nivel_confianza = Column(Numeric(3, 2))

    hora_inicio = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc).replace(microsecond=0),
        nullable=False
    )
    hora_fin = Column(DateTime(timezone=True), nullable=False)
    duracion_minutos = Column(SmallInteger, nullable=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(Text, nullable=False, unique=True)  # unicidad aquí
    password_hash = Column(Text, nullable=False)

    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    last_login = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("date_trunc('second', now())"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("date_trunc('second', now())"),
        server_onupdate=text("date_trunc('second', now())"),
        onupdate=func.now(), # pylint: disable=E1102
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("username", name="uq_usuario_username"),
        Index("ix_usuario_is_active", "is_active"),
    )

    # -------- API de contraseñas
    def set_password(self, password: str):
        if pwd_context is None:
            raise RuntimeError("pwd_context no inicializado. Importa tu contexto de passlib.")
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        if pwd_context is None:
            raise RuntimeError("pwd_context no inicializado. Importa tu contexto de passlib.")
        return pwd_context.verify(password, self.password_hash)

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("El username no puede estar vacío.")
        return username.strip()