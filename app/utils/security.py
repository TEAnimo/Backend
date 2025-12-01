import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","15"))  # 15 por defecto

def create_access_token(subject: str, minutes: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,           # mínimo: sujeto
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
