from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.api.router import api_router
from app.db.duckdb_conn import init_db

app = FastAPI(title="NYC Policy Feasibility Analyzer")

@app.on_event("startup")
def _startup():
    init_db()

# Serve API
app.include_router(api_router, prefix="/api")

# Serve static + templates (these paths assume your folders are at project root)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/ping")
def ping():
    return "pong"

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
