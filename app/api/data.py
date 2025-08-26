from fastapi import APIRouter, Query
from app.services.controllers import load_analysis_delta_table
from app.services import app_config

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/deg_analysis")
def get_delta(path: str = Query(default=app_config.DATA_PATHS.get("adeg")), limit: int = 20):
    return {"path": path, "rows": load_analysis_delta_table(path, limit=limit)}
