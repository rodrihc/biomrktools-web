from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from project root


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

from app.api.data import router as data_router

# Dash
import dash
from app.dash_app.layout import layout

app = FastAPI(title="biomrktools-web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# REST
app.include_router(data_router)

# Dash mounted at /dash
dash_app = dash.Dash(__name__, requests_pathname_prefix="/dash/")
dash_app.layout = layout
app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

