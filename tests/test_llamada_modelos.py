import joblib

def test_cargar_modelo_ml():
    """Prueba para cargar el modelo de ML desde el archivo 'model.pkl'"""
    modelo_ml = joblib.load("model.pkl")
    assert modelo_ml is not None  # Verifica que el modelo se cargó correctamente

def test_cargar_modelo_pca():
    """Prueba para cargar el modelo PCA desde el archivo 'pca_model.pkl'"""
    modelo_pca = joblib.load("pca_model.pkl")
    assert modelo_pca is not None  # Verifica que el modelo PCA se cargó correctamente

