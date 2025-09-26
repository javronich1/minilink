from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, unique=True)
    original_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    click_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None