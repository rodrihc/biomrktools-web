from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy

from app.dash_app.layout import serve_layout
from app.api import data

# FastAPI app
app = FastAPI(title="biomrktools-web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Include FastAPI API endpoints
app.include_router(data.router)

# Dash app
dash_app = DashProxy(
    __name__,
    requests_pathname_prefix="/dash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Set layout
dash_app.layout = serve_layout()

# Import callbacks AFTER layout is set so they register properly
from app.dash_app import callbacks

# Mount Dash onto FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))
