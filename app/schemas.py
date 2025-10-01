from datetime import datetime
from typing import Optional
from pydantic import BaseModel, AnyUrl

class LinkCreate(BaseModel):
    original_url: AnyUrl
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    label: Optional[str] = None

class LinkRead(BaseModel):
    short_code: str
    original_url: str
    label: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int
    last_accessed: Optional[datetime] = None

class LinkUpdate(BaseModel):
    original_url: Optional[AnyUrl] = None
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    label: Optional[str] = None

class StatsRead(BaseModel):
    click_count: int
    last_accessed: Optional[datetime]

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

class LoginForm(BaseModel):
    username: str
    password: str