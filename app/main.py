from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import playlists as playlists_router
from app.api import tracks as tracks_router

app = FastAPI(
    title="MoodTune API",
    version="0.1.0",
    description=(
        "API para gestionar playlists y tracks de MoodTune. "
        "\n- `finalize` requiere ≥ 20 tracks.\n- `bulkAdd` ignora duplicados.\n- Paginación por cursor en /playlists."
    ),
)

app.include_router(playlists_router.router)
app.include_router(tracks_router.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# Manejo simple de errores conocidos (opcional; FastAPI ya maneja HTTPException)
@app.exception_handler(Exception)
async def unhandled_exc(_):
    # Evita exponer secrets: solo mensaje genérico
    return JSONResponse(status_code=500, content={"detail": "internal_error"})
