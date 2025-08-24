from fastapi import APIRouter, Query
from app.services.storage import read_delta_head
from app.services.settings import settings

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/delta")
def get_delta(path: str = Query(default=settings.DELTA_PATH), limit: int = 20):
    return {"path": path, "rows": read_delta_head(path, limit=limit)}
