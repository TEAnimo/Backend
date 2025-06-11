import joblib
import pandas as pd

def test_transformacion_y_dimensiones_pca():
    """Prueba para realizar una transformación con el modelo PCA y verificar las dimensiones"""
    modelo_pca = joblib.load("pca_model.pkl")

    # Crear el DataFrame normalizado con las características esperadas
    ejemplo = {
        "A1": 0,
        "A2": 0,
        "A3": 1,
        "A4": 1,
        "A5": 1,
        "A6": 1,
        "A7": 1,
        "A8": 1,
        "A9": 1,
        "A10_Autism_Spectrum_Quotient": 1,
        "Age_Years": 0.7647,  
        "Qchat_10_Score": 0.8,
        "Speech_Delay_Language_Disorder": 0,
        "Learning_Disorder": 0,
        "Genetic_Disorders": 0,
        "Depression": 0,
        "Global_Developmental_Delay_Intellectual_Disability": 0,
        "Social_Behavioural_Issues": 0,
        "Anxiety_Disorder": 0,
        "Family_Mem_With_Asd": 0,
        "Comorbidity_%": 0,
        "Communication_Issues_%": 0.6,
        "Social_Interaction_Issues_%": 0.55,
        "Sex_M": 0,
        "Clinical_Profile_Mixed": 1,
        "Clinical_Profile_Social interaction": 0
    }

    # Convertir a un DataFrame con el orden correcto
    ordered_vars = [
        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10_Autism_Spectrum_Quotient",
        "Age_Years", "Qchat_10_Score", "Speech_Delay_Language_Disorder", "Learning_Disorder",
        "Genetic_Disorders", "Depression", "Global_Developmental_Delay_Intellectual_Disability",
        "Social_Behavioural_Issues", "Anxiety_Disorder", "Family_Mem_With_Asd", "Comorbidity_%",
        "Communication_Issues_%", "Social_Interaction_Issues_%", "Sex_M", "Clinical_Profile_Mixed",
        "Clinical_Profile_Social interaction"
    ]

    valores = [ejemplo[var] for var in ordered_vars]
    df_ejemplo = pd.DataFrame([valores], columns=ordered_vars)

    # Realizar la transformación usando el PCA
    transformacion = modelo_pca.transform(df_ejemplo)

    # Verifica que la transformación no sea None
    assert transformacion is not None

    # Verificar que la salida tenga el número correcto de componentes principales (en este caso, 2)
    assert transformacion.shape[1] == 2
