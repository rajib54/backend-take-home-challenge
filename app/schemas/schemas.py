from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    long_url: str

class URLResponse(BaseModel):
    slug: str
    short_url: str

class URLStats(BaseModel):
    slug: str
    long_url: str
    visits: int
    last_visit: Optional[datetime]