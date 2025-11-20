from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Evaluacion
from app.schemas.input_data import InputArray
from app.model.data_preprocessor import DataPreprocessor
from app.utils.email_sender import enviar_pdf_por_correo
from app.utils.conversion import sanitize_numpy_types
from app.model.predictor import predecir
from pydantic import EmailStr
from app.utils.email_config import conf  # configuración separada
from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile
import shutil
import math
import os

router = APIRouter()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/predict")
def predict(data: InputArray, db: Session = Depends(get_db)):
    if len(data.values) != 25:
        return {"error": f"Se esperaban 25 valores y se recibieron {len(data.values)}"}

    # Procesamiento y predicción
    processor = DataPreprocessor(data.values)
    feature_vector = processor.get_feature_vector()
    resultado = predecir(feature_vector)

    # Preparar y sanear datos
    data_dict = processor.preparar_data_para_guardar(resultado)
    data_dict = sanitize_numpy_types(data_dict)

    evaluacion = Evaluacion(**data_dict)

    # Obtener hora actual en Lima y asignarla como hora_fin
    lima = ZoneInfo("America/Lima")
    hora_actual = datetime.now(lima).replace(microsecond=0)
    evaluacion.hora_fin = hora_actual

    #Calcular duración en minutos
    if evaluacion.hora_inicio:
        diferencia = hora_actual - evaluacion.hora_inicio
        minutos = diferencia.total_seconds() / 60
        evaluacion.duracion_minutos = math.ceil(minutos)

    # Guardar en BD
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)

    return {
        "clase_predicha": resultado["clase_predicha"],
        "riesgo_autismo": resultado["riesgo_autismo"]
    }


@router.post("/enviar-pdf")
async def enviar_pdf(
    file: UploadFile = File(...),
    destinatario: EmailStr = Form(...)
):
    # Crear ruta con nombre original del archivo
    temp_dir = tempfile.gettempdir()
    final_path = os.path.join(temp_dir, file.filename)

    with open(final_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await enviar_pdf_por_correo(final_path, destinatario, conf)

    os.remove(final_path)

    return JSONResponse(content={"mensaje": f"Informe de evaluación enviado correctamente a {destinatario}"})
