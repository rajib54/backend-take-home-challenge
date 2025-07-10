from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import URLStats
from app.services import report as report_service
from typing import List

router = APIRouter()

@router.get("/stats", response_model=List[URLStats])
def stats(db: Session = Depends(get_db), limit: int = 10) -> List[URLStats]:
    return report_service.get_top_urls(db, limit)

@router.get("/stats/{slug}", response_model=URLStats)
def stats_for_slug(slug: str, db: Session = Depends(get_db)) -> URLStats:
    stats = report_service.get_url_stats(db, slug)
    if not stats:
        raise HTTPException(status_code=404, detail="Slug not found or has no visits")
    return stats