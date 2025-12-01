from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api, auth, dashboard
# Para crear las tablas en Railway (solo la primera vez o si no existen)
from app.db.models import Base
from app.db.init_db import init_usuario_default
from app.db.database import engine

# Crear automáticamente las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api.router)
app.include_router(auth.router)
app.include_router(dashboard.router)

init_usuario_default()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://octopus-app-wuqzz.ondigitalocean.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
