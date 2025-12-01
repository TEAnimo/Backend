from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import Usuario
from app.db.database import SessionLocal

# Usuario admin por defecto
USUARIO_DEFAULT = {
    "username": "ECastro",
    "password_plano": "Admin123",
}

def crear_usuario_default(db: Session) -> Usuario:
    existente = (
        db.query(Usuario)
          .filter(Usuario.username == USUARIO_DEFAULT["username"])
          .first()
    )
    if existente:
        print("Usuario ADMIN por defecto ya existe.")
        return existente

    admin = Usuario(
        username=USUARIO_DEFAULT["username"],
        is_active=True,
    )
    admin.set_password(USUARIO_DEFAULT["password_plano"])
    db.add(admin)

    try:
        db.commit()
        db.refresh(admin)
        print("Usuario ADMIN por defecto creado.")
        return admin
    except IntegrityError as ie:
        db.rollback()
        # Posible carrera: otro proceso lo creó entre el check y el commit
        print(f"Colisión de unicidad al crear el admin por defecto: {ie}")
        return (
            db.query(Usuario)
              .filter(Usuario.username == USUARIO_DEFAULT["username"])
              .first()
        )

def init_usuario_default():
    # Usa context manager para asegurar cierre de sesión
    db: Session = SessionLocal()
    try:
        crear_usuario_default(db)
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar usuario admin: {e}")
        raise
    finally:
        db.close()
