# app/api/deps_auth.py
from typing import Optional, Tuple
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from app.core.auth_settings import COOKIE_NAME, COOKIE_MAX_AGE, SAMESITE, SECURE_COOKIE, RENEW_THRESHOLD_SECONDS
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Usuario
from app.utils.security import SECRET_KEY, ALGORITHM, create_access_token

# Permite que falte el header Authorization para poder usar cookie como fallback
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _decode_token_return_sub_exp(token: str) -> Tuple[str, int]:
    """
    Devuelve (sub, exp_ts). Lanza 401 si token inválido/expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        exp = payload.get("exp")
        if not sub or not exp:
            raise JWTError("missing-claims")
        return sub, int(exp)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

def get_current_user(
    request: Request,
    response: Response,
    bearer: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    # 1) Cookie HTTPOnly (preferente)
    token = request.cookies.get(COOKIE_NAME)

    # 2) Fallback: Authorization: Bearer <token>
    if not token and bearer:
        token = bearer

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username, exp_ts = _decode_token_return_sub_exp(token)

    # Carga del usuario
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3) Sliding session: refrescar token si faltan pocos minutos (o siempre)
    now_ts = int(datetime.now(timezone.utc).timestamp())
    remaining = exp_ts - now_ts

    if remaining <= RENEW_THRESHOLD_SECONDS:
        new_token = create_access_token(subject=user.username)  # +15 min desde ahora
        # Refresca cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=new_token,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=SECURE_COOKIE,
            samesite=SAMESITE,
            path="/",
        )
        # (Opcional) Si algún cliente usa Bearer, puedes mandarlo en un header propio:
        response.headers["X-Refreshed-Token"] = new_token

    return user
