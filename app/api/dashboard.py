from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Evaluacion
from sqlalchemy import func
from app.schemas.input_data import EvaluacionResponse, DatosDashboardResponse
from app.db.models import Usuario
from app.api.deps_auth import get_current_user
from datetime import datetime
from typing import Optional  # Importar Optional desde typing

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/evaluaciones", response_model=dict)
def list_evaluaciones(
    start_date: datetime = Query(None),  # Filtro de fecha de inicio
    end_date: datetime = Query(None),    # Filtro de fecha de fin
    tiene_tea: Optional[bool] = Query(None),  # Filtro de TEA (True/False)
    skip: int = Query(0),                # Paginación: Saltar los primeros N elementos
    limit: int = Query(5),              # Paginación: Limitar a 10 elementos por página
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Validación del usuario autenticado
):
    query = db.query(Evaluacion)

    # Filtro por fecha
    if start_date:
        query = query.filter(Evaluacion.hora_inicio >= start_date)
    # Filtro por fecha de fin
    if end_date:
        # Asegurarse de que la fecha de fin incluya hasta el final del día (23:59:59)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        query = query.filter(Evaluacion.hora_fin <= end_date)

    # Filtro por TEA
    if tiene_tea is not None:
        tea_value = 'Si' if tiene_tea else 'No'
        query = query.filter(Evaluacion.rasgos_tea == tea_value)

    # Seleccionar solo las columnas necesarias
    query = query.with_entities(
        Evaluacion.id,
        Evaluacion.hora_fin,
        Evaluacion.edad,
        Evaluacion.sexo,
        Evaluacion.qchat_resultado,
        Evaluacion.porc_deficiencia_social_interactiva,
        Evaluacion.porc_deficiencia_comunicativa,
        Evaluacion.perfil_clinico,
        Evaluacion.rasgos_tea,
        Evaluacion.nivel_confianza
    )

    # Paginación
    evaluaciones = query.offset(skip).limit(limit).all()

    # Convertir las filas de SQLAlchemy a un formato que FastAPI pueda manejar
    evaluaciones_dict = [EvaluacionResponse.from_orm(evaluacion).dict() for evaluacion in evaluaciones]

    # Contar el total de evaluaciones sin los filtros de paginación
    total_evaluaciones = query.count()

    # Calcular el total de páginas
    total_paginas = (total_evaluaciones // limit) + (1 if total_evaluaciones % limit > 0 else 0)

    return {
        "evaluaciones": evaluaciones_dict,
        "total": total_evaluaciones,
        "total_paginas": total_paginas
    }

@router.get("/evaluacion/{evaluacion_id}")
def get_evaluacion_detallada(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Validación del usuario autenticado
):
    evaluacion = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    return {"evaluacion": evaluacion}

@router.get("/dashboard/datos", response_model=DatosDashboardResponse)
def obtener_datos_dashboard(
    start_date: datetime = Query(None),  # Filtro de fecha de inicio
    end_date: datetime = Query(None),    # Filtro de fecha de fin
    tiene_tea: Optional[bool] = Query(None),  # Filtro de TEA (True/False)
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Validación del usuario autenticado
):
    # Normalizar la fecha de fin para incluir todo el día
    if end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59)  # Aseguramos que se considere todo el día

    # Base query
    query = db.query(Evaluacion)

    # Filtros por fecha y TEA
    if start_date:
        query = query.filter(Evaluacion.hora_inicio >= start_date)
    if end_date:
        query = query.filter(Evaluacion.hora_fin <= end_date)
    if tiene_tea is not None:
        tea_value = 'Si' if tiene_tea else 'No'
        query = query.filter(Evaluacion.rasgos_tea == tea_value)
    # pylint: disable=E1102
    # 1. Diagrama de barras para perfil de TEA detectado (perfil_clinico)
    perfil_tea = query.with_entities(Evaluacion.perfil_clinico, func.count(Evaluacion.id).label('count')) \
                      .group_by(Evaluacion.perfil_clinico) \
                      .all()

    # 2. Histograma con puntaje de QCHAT 10 (qchat_resultado)
    qchat_scores = query.with_entities(Evaluacion.qchat_resultado).all()

    # 3. Gráfico de pastel para cantidad de niños con TEA y sin TEA detectados
    tea_pastel = query.with_entities(Evaluacion.rasgos_tea, func.count(Evaluacion.id).label('count')) \
                       .group_by(Evaluacion.rasgos_tea) \
                       .all()

    # 4. Gráfico de pastel para cantidad de niños por sexo
    sexo_pastel = query.with_entities(Evaluacion.sexo, func.count(Evaluacion.id).label('count')) \
                        .group_by(Evaluacion.sexo) \
                        .all()

    # Retornar los datos de los gráficos en el formato adecuado
    return DatosDashboardResponse(
        perfil_tea=perfil_tea,  # Datos para el gráfico de barras
        qchat_scores=[score[0] for score in qchat_scores],  # Puntajes de QCHAT
        tea_pastel=tea_pastel,  # Datos para el gráfico de pastel TEA vs No TEA
        sexo_pastel=sexo_pastel  # Datos para el gráfico de pastel por sexo
    )