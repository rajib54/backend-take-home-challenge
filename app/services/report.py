from sqlalchemy.orm import Session
from app.handler import report as report_handler

def get_url_stats(db: Session, slug: str):
    """Service: Get detailed stats for a specific slug."""
    return report_handler.get_stats_for_slug(db, slug)

def get_top_urls(db: Session, limit: int = 10):
    """Service: Get top visited slugs."""
    return report_handler.get_top_urls(db, limit)
