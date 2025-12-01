from pydantic import BaseModel
from typing import List, Union, Optional, Tuple
from datetime import datetime

class InputArray(BaseModel):
    values: List[Union[int, float, str]]

class EvaluacionResponse(BaseModel):
    id: int
    hora_fin: datetime
    edad: Optional[int]
    sexo: Optional[str]
    qchat_resultado: Optional[int]
    porc_deficiencia_social_interactiva: Optional[float]
    porc_deficiencia_comunicativa: Optional[float]
    perfil_clinico: Optional[str]
    rasgos_tea: Optional[str]
    nivel_confianza: Optional[float]

    class Config:
        from_attributes = True  # Habilitar la extracción de atributos directamente de los objetos ORM

class DatosDashboardResponse(BaseModel):
    # Datos para el gráfico de barras de 'perfil_tea'
    perfil_tea: List[Tuple[str, int]]  # Una lista de tuplas (perfil_clinico, count)
    
    # Datos para el histograma de 'qchat_scores'
    qchat_scores: List[int]  # Lista de puntajes de QCHAT
    
    # Datos para el gráfico de pastel 'tea_pastel' (TEA vs No TEA)
    tea_pastel: List[Tuple[str, int]]  # Una lista de tuplas ('Si'/'No', count)
    
    # Datos para el gráfico de pastel 'sexo_pastel' (masculino/femenino)
    sexo_pastel: List[Tuple[str, int]]  # Una lista de tuplas ('M'/'F', count)

    class Config:
        from_attributes = True  # Permite la conversión de objetos ORM a Pydantic