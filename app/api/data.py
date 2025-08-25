from fastapi import APIRouter, Query
from app.services.storage import read_delta_head
from app.services.settings import settings
from app.services import app_config

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/deg_analysis")
def get_delta(path: str = Query(default=app_config.DATA_PATHS.get("adeg")), limit: int = 20):
    return {"path": path, "rows": read_delta_head(path, limit=limit)}
