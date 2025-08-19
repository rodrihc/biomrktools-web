from fastapi import APIRouter, Query
from app.services.storage import read_json_from_adls, read_delta_head
from app.services.settings import settings

router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/json")
def get_json(path: str = Query(default=settings.JSON_PATH)):
    return {"path": path, "data": read_json_from_adls(path)}

@router.get("/delta")
def get_delta(path: str = Query(default=settings.DELTA_PATH), limit: int = 20):
    return {"path": path, "rows": read_delta_head(path, limit=limit)}
