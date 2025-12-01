from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Routers
from app.api import api, auth, dashboard

# DB
from app.db.models import Base
from app.db.init_db import init_usuario_default
from app.db.database import engine

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)
init_usuario_default()

app = FastAPI()

# --- Rutas API ---
app.include_router(api.router)
app.include_router(auth.router)
app.include_router(dashboard.router)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://personal.teanimo.tech",   # Frontend DigitalOcean
        "https://page.teanimo.tech",       # Frontend interno
        "http://localhost:5173",           # Dev local
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ARCHIVOS ESTÁTICOS (page interno) ---
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

# --- SERVIR SPA (page interno) ---
@app.get("/")
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str = None):
    return FileResponse(os.path.join("app", "frontend", "index.html"))
