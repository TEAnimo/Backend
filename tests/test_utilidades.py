import numpy as np
from app.utils.conversion import sanitize_numpy_types

def test_sanitize_numpy_types():
    """Prueba para la función sanitize_numpy_types"""
    
    # Diccionario de ejemplo con tipos numpy
    data = {
        "col1": np.float64(3.14),
        "col2": np.int64(10),
        "col3": 20  # Ya es un int, no debe cambiar
    }
    
    # Llamar la función
    sanitized_data = sanitize_numpy_types(data)
    
    # Verificar que los tipos sean correctos
    assert isinstance(sanitized_data["col1"], float)
    assert isinstance(sanitized_data["col2"], int)
    assert isinstance(sanitized_data["col3"], int)


import os
from app.utils.email_config import ConnectionConfig

def test_connection_config():
    """Prueba para la configuración de la conexión de correo"""
    
    # Configurar variables de entorno temporalmente para la prueba
    os.environ["MAIL_USERNAME"] = "test_user"
    os.environ["MAIL_PASSWORD"] = "test_password"
    os.environ["MAIL_SERVER"] = "smtp.example.com"
    os.environ["MAIL_PORT"] = "587"
    
    # Convertir la cadena 'True'/'False' a booleano
    os.environ["MAIL_STARTTLS"] = "False"  # O "True"
    os.environ["MAIL_SSL_TLS"] = "False"   # O "True"
    
    os.environ["MAIL_FROM"] = "test@example.com"
    
    # Función para convertir cadenas 'True'/'False' en booleanos
    def str_to_bool(value: str) -> bool:
        return value.lower() == "true"

    # Crear la configuración
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT")),
        MAIL_STARTTLS=str_to_bool(os.getenv("MAIL_STARTTLS")),
        MAIL_SSL_TLS=str_to_bool(os.getenv("MAIL_SSL_TLS")),
        MAIL_FROM=os.getenv("MAIL_FROM")
    )
    
    # Verificar que la configuración fue cargada correctamente
    assert conf.MAIL_USERNAME == "test_user"
    assert conf.MAIL_PASSWORD.get_secret_value() == "test_password"  # Acceder al valor real de la contraseña
    assert conf.MAIL_SERVER == "smtp.example.com"
    assert conf.MAIL_PORT == 587
    assert conf.MAIL_STARTTLS is False  # Debería ser False ahora
    assert conf.MAIL_SSL_TLS is False  # Debería ser False ahora
    assert conf.MAIL_FROM == "test@example.com"
