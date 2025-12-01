import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Leer la URL de conexión de Heroku
DATABASE_URL = os.getenv("DATABASE_URL")

# Heroku entrega postgres:// pero SQLAlchemy exige postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)

# Configurar sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
Base = declarative_base()
