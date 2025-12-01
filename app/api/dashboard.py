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

@router.get("/evaluaciones", response_model=dict)  #Se usa a la par del endpoint de datos dashboard
def list_evaluaciones(
    start_date: datetime = Query(None),  # Filtro de fecha de inicio
    end_date: datetime = Query(None),    # Filtro de fecha de fin
    tiene_tea: Optional[bool] = Query(None),  # Filtro de TEA (True/False)
    perfil_tea: Optional[str] = Query(None, enum=["mixto", "interactivo-social", "comunicativo"]),  # Filtro de perfil_tea
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

            # Filtro por perfil_tea
    if perfil_tea:
        query = query.filter(Evaluacion.perfil_clinico == perfil_tea)

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
        Evaluacion.nivel_confianza #Viene a ser tambien el riesgo de TEA
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

@router.get("/buscar_evaluacion/{evaluacion_id}", response_model=dict)
def get_evaluacion_tabla(
    evaluacion_id: int,  # ID de la evaluación a buscar
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Validación del usuario autenticado
):
    # Realizar la búsqueda de la evaluación por ID
    query = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id)

    # Seleccionar solo las columnas necesarias (usando with_entities)
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
        Evaluacion.nivel_confianza  # El riesgo de TEA
    )

    # Obtener el resultado de la consulta
    evaluacion = query.first()

    # Si no se encuentra la evaluación, lanzar un error 404
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    # Convertir la tupla en un diccionario con los valores relevantes
    evaluacion_dict = {
        "id": evaluacion.id,
        "hora_fin": evaluacion.hora_fin,
        "edad": evaluacion.edad,
        "sexo": evaluacion.sexo,
        "qchat_resultado": evaluacion.qchat_resultado,
        "porc_deficiencia_social_interactiva": evaluacion.porc_deficiencia_social_interactiva,
        "porc_deficiencia_comunicativa": evaluacion.porc_deficiencia_comunicativa,
        "perfil_clinico": evaluacion.perfil_clinico,
        "rasgos_tea": evaluacion.rasgos_tea,
        "nivel_confianza": evaluacion.nivel_confianza
    }

    # Retornar la evaluación como un diccionario con las columnas necesarias
    return {"evaluacion": evaluacion_dict}


@router.get("/evaluacion_detalle/{evaluacion_id}")
def get_evaluacion_detallada(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Validación del usuario autenticado
):
    evaluacion = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    return {"evaluacion": evaluacion}

@router.get("/dashboard/datos", response_model=DatosDashboardResponse) #Se usa a la par del endpoint de list_evaluaciones
def get_datos_dashboard(
    start_date: datetime = Query(None),  # Filtro de fecha de inicio
    end_date: datetime = Query(None),    # Filtro de fecha de fin
    tiene_tea: Optional[bool] = Query(None),  # Filtro de TEA (True/False)
    perfil_tea: Optional[str] = Query(None, enum=["mixto", "interactivo-social", "comunicativo"]),  # Filtro de perfil_tea
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
    # Filtro por perfil_tea
    if perfil_tea:
        query = query.filter(Evaluacion.perfil_clinico == perfil_tea)

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