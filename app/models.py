from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# represents user registered in app, with id (primary key), username (unique), and password hash
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str  

# represents a shortened link, with various fields including foreign key to User
class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, unique=True)
    original_url: str
    label: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    click_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")