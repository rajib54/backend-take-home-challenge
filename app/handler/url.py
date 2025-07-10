from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.urls import URL
from app.models.visit import Visit
from app.models.sequence import SlugSequence
import logging

logger = logging.getLogger(__name__)

def get_url_by_slug(db: Session, slug: str) -> URL | None:
    """Retrieve a URL object by its slug."""
    try:
        return db.query(URL).filter(URL.slug == slug).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching slug '{slug}': {e}")
        raise RuntimeError("Database error while fetching slug")

def get_url_by_long_url(db: Session, long_url: str) -> URL | None:
    """Retrieve a URL object by its original long URL."""
    try:
        return db.query(URL).filter(URL.long_url == long_url).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching long_url '{long_url}': {e}")
        raise RuntimeError("Database error while fetching long URL")

def create_url(db: Session, slug: str, long_url: str) -> URL:
    """Create a new URL object."""
    try:
        db_url = URL(slug=slug, long_url=long_url)
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        return db_url
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating URL for slug '{slug}': {e}")
        raise RuntimeError("Database error while creating URL")

def create_visit(db: Session, url_id: int) -> Visit:
    """Create a visit record for a given URL."""
    try:
        visit = Visit(url_id=url_id)
        db.add(visit)
        db.commit()
        return visit
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error logging visit for url_id '{url_id}': {e}")
        raise RuntimeError("Database error while creating visit")

def get_slug_sequence(db: Session, lock: bool = False) -> SlugSequence | None:
    """Fetch the current slug sequence, with optional row locking."""
    try:
        query = db.query(SlugSequence)
        if lock:
            query = query.with_for_update()
        return query.first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching slug sequence: {e}")
        raise RuntimeError("Database error while fetching slug sequence")

def set_slug_sequence(db: Session, value: int) -> SlugSequence:
    """Update or initialize the slug sequence counter."""
    try:
        record = db.query(SlugSequence).first()
        if record:
            record.current_value = value
        else:
            record = SlugSequence(current_value=value)
            db.add(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error setting slug sequence to {value}: {e}")
        raise RuntimeError("Database error while updating slug sequence")
