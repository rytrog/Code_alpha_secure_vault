from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .startup import on_startup
from .shutdown import on_shutdown
from .security.middleware import SecurityMiddleware
from .api import auth, users, vault, attacks, dashboard, ai, reports, health

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Cloud Secure Data Vault & SQL Injection Defense Platform",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware (SQL Injection Detection + Rate Limiting)
app.add_middleware(SecurityMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vault.router)
app.include_router(attacks.router)
app.include_router(dashboard.router)
app.include_router(ai.router)
app.include_router(reports.router)
app.include_router(health.router)


from fastapi.staticfiles import StaticFiles
import os

@app.on_event("startup")
def startup_event():
    on_startup()


@app.on_event("shutdown")
def shutdown_event():
    on_shutdown()


# Mount static frontend files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
