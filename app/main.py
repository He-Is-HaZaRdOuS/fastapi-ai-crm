from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from sqlmodel import Session
from contextlib import asynccontextmanager

from app.api import router as api_router
from app.core.init_rbac import init_rbac
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as session:
        pass
        # init_rbac(session, "configuration/rbac_config.toml")
    yield

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
