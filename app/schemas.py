from datetime import datetime
from typing import Optional
from pydantic import BaseModel, AnyUrl

# schema for creating a new shortened link (POST /api/links)
class LinkCreate(BaseModel):
    original_url: AnyUrl
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    label: Optional[str] = None

# schema for reading a shortened link (GET /api/links/{short_code})
class LinkRead(BaseModel):
    short_code: str
    original_url: str
    label: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int
    last_accessed: Optional[datetime] = None

# schema for updating a shortened link (PATCH /api/links/{short_code})
class LinkUpdate(BaseModel):
    original_url: Optional[AnyUrl] = None
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    label: Optional[str] = None

# schema for link statistics (GET /api/links/{short_code}/stats)
class StatsRead(BaseModel):
    click_count: int
    last_accessed: Optional[datetime]

# schema for creating a new user (POST /api/users)
class UserCreate(BaseModel):
    username: str
    password: str

# schema for reading user info (GET /api/users/{user_id})
class UserRead(BaseModel):
    id: int
    username: str

# schema for user login (POST /api/login)
class LoginForm(BaseModel):
    username: str
    password: str