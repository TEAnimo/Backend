from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api
# Para crear las tablas en Railway (solo la primera vez o si no existen)
from app.db.models import Base
from app.db.init_db import init_usuario_default
from app.db.database import engine

# Crear automáticamente las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

init_usuario_default()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://teanimo.vercel.app",     # Producción
        "http://localhost:3000"           # Desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)