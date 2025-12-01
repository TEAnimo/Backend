from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth_settings import COOKIE_NAME, COOKIE_MAX_AGE, SAMESITE, SECURE_COOKIE
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Usuario
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(response: Response, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form.username).first()
    if not user or not user.verify_password(form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )


    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    token = create_access_token(subject=user.username)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=SECURE_COOKIE,   # False en local, True en prod
        samesite=SAMESITE,      # "lax" mismo dominio; "none" si front y API en dominios distintos (requiere secure=True)
        path="/",
    )
    return {"access_token": token, "token_type": "bearer"}  # soporta ambos modos

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Sesión cerrada"}
