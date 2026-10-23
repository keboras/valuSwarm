"""Register Integrity Engine routes and startup on an existing FastAPI app."""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.database import get_db, init_db
from backend.routers import dashboard, intake, memory, mirror_interactions, omni, reputation, studio, user
from backend.seed import seed_unlocks

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def register_mechanical_routes(app: FastAPI) -> None:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:8090",
            "http://localhost:8090",
            "http://127.0.0.1:8091",
            "http://localhost:8091",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(memory.router)
    app.include_router(reputation.router)
    app.include_router(dashboard.router)
    app.include_router(user.router)
    app.include_router(intake.router)
    app.include_router(mirror_interactions.router)
    app.include_router(studio.router)
    app.include_router(omni.router)

    from backend.services.literacy_content import get_modules

    @app.get("/literacy/modules", tags=["literacy"])
    def literacy_modules_public():
        return {"modules": get_modules()}

    @app.get("/literacy/playbook", tags=["literacy"])
    def literacy_playbook_public(category: str | None = None, tag: str | None = None):
        from backend.services.wealth_playbook import PLAYBOOK_CATEGORIES, get_playbook

        if category and category not in PLAYBOOK_CATEGORIES:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="Invalid category")
        return {"categories": list(PLAYBOOK_CATEGORIES), "entries": get_playbook(category=category, tag=tag)}

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/static/index.html")

    @app.get("/reputation/character-mirror", tags=["reputation"])
    def reputation_character_mirror_alias(
        user_id: str = "default",
        essentials_pct: float = 65.0,
        life_bucket_pct: float = 20.0,
        stability_fund_pct: float = 0.0,
        money_velocity_tier: str = "B",
        consumer_tag_count: int = 0,
        acquirer_tag_count: int = 0,
        pause_breaches_recent: int = 0,
        db=Depends(get_db),
    ):
        """Alias for GET /dashboard/mirror (plan-compatible path)."""
        from backend.routers.dashboard import get_character_mirror

        return get_character_mirror(
            user_id=user_id,
            essentials_pct=essentials_pct,
            life_bucket_pct=life_bucket_pct,
            stability_fund_pct=stability_fund_pct,
            money_velocity_tier=money_velocity_tier,
            consumer_tag_count=consumer_tag_count,
            acquirer_tag_count=acquirer_tag_count,
            pause_breaches_recent=pause_breaches_recent,
            db=db,
        )

    if FRONTEND_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

    @app.get("/health/mechanical")
    def mechanical_health():
        return {"status": "ok", "service": "integrity-engine"}

    @app.get("/advisor/status")
    def advisor_status():
        err = getattr(app.state, "advisor_error", None)
        if err:
            return {"available": False, "message": "advisor unavailable"}
        return {"available": True, "message": "advisor ready"}

    @app.exception_handler(Exception)
    async def _hide_tracebacks(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return await http_exception_handler(request, exc)
        if "text/html" in (request.headers.get("accept") or ""):
            return HTMLResponse("<p>Something went wrong.</p>", status_code=500)
        return JSONResponse({"detail": "Something went wrong."}, status_code=500)

    @app.on_event("startup")
    def _mechanical_startup():
        init_db()
        seed_unlocks()


def create_mechanical_app() -> FastAPI:
    """Standalone mechanical API (e.g. tests or separate process)."""
    from fastapi import FastAPI

    app = FastAPI(
        title="Architect Blueprint Mechanical API",
        version="1.0.0",
    )
    register_mechanical_routes(app)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "mechanical-api"}

    return app
