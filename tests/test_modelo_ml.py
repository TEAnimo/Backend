import joblib
import pandas as pd

def test_predicciones_ml():
    """Prueba para realizar predicciones con el modelo de ML"""
    modelo_ml = joblib.load("model.pkl")

    # Crear un diccionario con las características según el formato de entrada
    ejemplo = {
        "PCA_1": -0.2958,
        "A6": 1,
        "A9": 1,
        "Social_Interaction_Issues_%": 0.55,
        "A7": 1,
        "A5": 1,
        "Qchat_10_Score": 0.8,
        "Communication_Issues_%": 0.6,
        "A4": 1,
        "A1": 0,
        "A2": 0,
        "A8": 1,
        "Sex_M": 0,
        "A3": 1,
        "Global_Developmental_Delay_Intellectual_Disability": 0,
        "Speech_Delay_Language_Disorder": 0,
        "Depression": 0,
        "Social_Behavioural_Issues": 0,
        "Anxiety_Disorder": 0,
        "Comorbidity_%": 0
    }

    # Convertir el diccionario en un DataFrame de pandas para que tenga los nombres de las características
    # Asegúrate de que las columnas estén en el mismo orden que las usadas para entrenar el modelo
    ordered_vars = [
        "PCA_1", "A6", "A9", "Social_Interaction_Issues_%", "A7", "A5", "Qchat_10_Score",
        "Communication_Issues_%", "A4", "A1", "A2", "A8", "Sex_M", "A3",
        "Global_Developmental_Delay_Intellectual_Disability", "Speech_Delay_Language_Disorder",
        "Depression", "Social_Behavioural_Issues", "Anxiety_Disorder", "Comorbidity_%"
    ]
    
    # Crear un DataFrame con los valores, usando las columnas correspondientes
    df_ejemplo = pd.DataFrame([ejemplo], columns=ordered_vars)

    # Realizar la predicción con el modelo de ML
    prediccion = modelo_ml.predict(df_ejemplo)
    
    assert prediccion is not None  # Verifica que la predicción no sea None
    assert len(prediccion) == 1  # Verifica que la predicción sea un solo valor
    assert prediccion[0] in [0, 1]  # Verifica que la predicción esté dentro del rango esperado (ajusta según tu caso)



def test_predicciones_ml_api():
    """Prueba para realizar predicciones con la API de predicción"""
    data = {
       "values": [14,0,0,0,1,1,1,1,1,1,1,1,8,0,0,0,0,0,0,0,0,55,60,"11/5/2025, 3:08:53 p. m.","11/5/2025, 3:09:44 p. m."]
    }

    # Asegurarnos de que la predicción devuelva resultados correctos usando el modelo en el API
    from fastapi.testclient import TestClient
    from app.api import router

    client = TestClient(router)

    response = client.post("/predict", json=data)
    assert response.status_code == 200
    assert "clase_predicha" in response.json()
    assert "riesgo_autismo" in response.json()
