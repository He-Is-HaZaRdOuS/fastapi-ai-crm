import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from sqlmodel import Session

from app.api import router as api_router
from app.core.init_rbac import init_rbac
from app.core.queue import start_workers
from app.core.summarizer import summarizer
from app.db.session import engine
from app.models.note import *
from app.models.rbac import *
from app.models.user import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load summarization model once
    app.state.summarizer = summarizer
    with Session(engine) as session:
        # pass
        init_rbac(session, "configuration/rbac_config.toml")

    # Start background workers
    app.state.worker_tasks = await start_workers(num_workers=2)

    try:
        yield
    finally:
        # Shutdown workers on app exit
        for task in app.state.worker_tasks:
            task.cancel()
        await asyncio.gather(*app.state.worker_tasks, return_exceptions=True)


app = FastAPI(title="FastAPI AI Mini-CRM", lifespan=lifespan)


# @app.on_event("startup")
# def startup_event():
#     with Session(engine) as session:
#         init_rbac(session, "configuration/rbac_config.toml")


app.include_router(api_router)

favicon_path = "favicon.ico"


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    return f"""
        <html>
            <head><title>Welcome</title></head>
            <body>
                <h1>Welcome to the FastAPI</h1>
                <p>Please visit the <a href="{app.docs_url}">API documentation</a> for more information.</p>
            </body>
        </html>
    """
