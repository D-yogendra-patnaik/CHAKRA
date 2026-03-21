import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as v1_router
from src.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Zero-trust proxy and AI Guardrail Layer.",
        version="1.0.0",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Healthcheck
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "ok", "app": settings.APP_NAME}

    # Include API Routes
    app.include_router(v1_router, prefix="/v1", tags=["V1 API"])

    # Mount static dashboard files
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
