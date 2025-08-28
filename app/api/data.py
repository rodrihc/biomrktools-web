from fastapi import APIRouter, Query
from app.services.controllers import load_analysis_delta_table
from app.services import app_config

router = APIRouter(prefix="/api/data", tags=["data"])
âdeg_path = app_config.DATA_PATHS.get("adeg")

@router.get("/deg_analysis/{cancer_code}")
def get_delta(cancer_code: str, path: str = Query(default=âdeg_path), limit: int = 20):

    return {"path": path, "rows": load_analysis_delta_table(path,
         cancer_code=cancer_code, 
         limit=limit)}
