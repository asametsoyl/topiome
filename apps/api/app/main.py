from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .db import init_db
from .routers import (
    api_keys,
    auth,
    billing,
    compare,
    dashboard,
    disease_packs,
    health,
    org,
    projects,
    runs,
    samples,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    problems = settings.production_problems()
    if problems:
        raise RuntimeError("Refusing to start with unsafe settings: " + "; ".join(problems))
    init_db()
    if settings.queue_mode == "inline":
        # Inline runs live in this process; anything left over was lost in a restart.
        from .services.queue import recover_interrupted_runs

        recover_interrupted_runs()
    if settings.auto_seed and settings.is_dev:
        from .seed import ensure_seed

        ensure_seed()
    yield


app = FastAPI(
    title="Topiome API",
    version="0.1.0",
    description=(
        "Spatial disease atlas platform. **Research Use Only** — not for diagnosis, "
        "prognosis, treatment selection, or clinical decision-making."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not settings.is_dev:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"
        )
    return response


@app.middleware("http")
async def origin_check(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origin_list:
            return JSONResponse(status_code=403, content={"detail": "Origin not allowed"})
    return await call_next(request)


app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(disease_packs.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(samples.router, prefix="/api/v1")
# Before runs: `/runs/compare` must match ahead of `/runs/{run_id}`.
app.include_router(compare.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(org.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {
        "name": "Topiome API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "ruo": "For Research Use Only. Not for clinical decision-making.",
    }
