from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import pool
from app.routers import auth, users


app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

# If we have a Frontend Build Folder, serve it.
if settings.FRONTEND_BUILD_DIR is not None:
    BUILD_DIR = Path(settings.FRONTEND_BUILD_DIR)
    templates = Jinja2Templates(directory=BUILD_DIR.as_posix())

    app.mount(
        "/static/",
        StaticFiles(directory=BUILD_DIR / "static"),
        name="React App static files",
    )

    @app.get("/{full_path:path}")
    async def serve_react_app(request: Request, full_path: str):
        return templates.TemplateResponse("index.html", {"request": request})


# Otherwise add CORS support
else:
    origins = ["http://localhost:3000", "localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def open_pool():
    pool.open()


@app.on_event("shutdown")
def close_pool():
    pool.close()
