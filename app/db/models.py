from sqlalchemy import Column, Integer, SmallInteger, String, Numeric, CHAR, DateTime
from datetime import datetime, timezone
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
