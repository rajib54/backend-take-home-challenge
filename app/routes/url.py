from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import URLCreate, URLResponse
from app.services import url as url_service
from app.core.config import settings

router = APIRouter()

@router.post("/shorten", response_model=URLResponse)
def shorten(payload: URLCreate, db: Session = Depends(get_db)) -> URLResponse:
    url = url_service.create_or_get_short_url(db, payload.long_url)
    return URLResponse(slug=url.slug, short_url=f"{settings.BASE_URL}/{url.slug}")

@router.get("/{slug}")
def redirect(slug: str, db: Session = Depends(get_db)) -> RedirectResponse:
    url = url_service.resolve_slug_and_record_visit(db, slug)
    if not url or not url.long_url:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=url.long_url, status_code=307)