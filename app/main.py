from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api import api, auth, dashboard

# DB
from app.db.models import Base
from app.db.init_db import init_usuario_default
from app.db.database import engine

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registrar routers
app.include_router(api.router)
app.include_router(auth.router)
app.include_router(dashboard.router)

# Inicializar usuario admin por defecto (si aplica)
init_usuario_default()

# CORS – permite ambos frontends + localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://personal.teanimo.tech",
        "https://page.teanimo.tech",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
