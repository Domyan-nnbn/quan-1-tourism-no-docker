from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlsplit

class Login(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=200)

class POIInput(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    name_en: str = Field(min_length=2, max_length=150)
    category: Literal['heritage','culture','landmark','food','nature']
    address: str = Field(min_length=2, max_length=250)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius: int = Field(default=30, ge=10, le=500)
    source_url: str = Field(default='', max_length=1000)

    @field_validator('name','name_en','address')
    @classmethod
    def nonempty(cls, v):
        if not v.strip(): raise ValueError('Cannot be blank')
        return v.strip()

    @field_validator('source_url')
    @classmethod
    def wiki_only(cls, v):
        if not v: return v
        u = urlsplit(v)
        if u.scheme != 'https' or u.netloc not in ('vi.wikipedia.org','en.wikipedia.org') or not u.path.startswith('/wiki/') or len(u.path)<=6 or u.query or u.fragment:
            raise ValueError('Use https://vi.wikipedia.org/wiki/... or https://en.wikipedia.org/wiki/...')
        return v

class DraftInput(BaseModel):
    vi: str = Field(min_length=20, max_length=12000)
    en: str = Field(default='', max_length=12000)
    zh: str = Field(default='', max_length=12000)
    fr: str = Field(default='', max_length=12000)
    ja: str = Field(default='', max_length=12000)

class ConsentInput(BaseModel):
    granted: bool
    policy: Literal['2026-01'] = '2026-01'

class EventInput(BaseModel):
    id: UUID
    poi_id: UUID
    kind: Literal['narration_started','narration_completed']
    locale: Literal['vi','en','zh','fr','ja']

class Register(BaseModel):
    name: str = Field(min_length=1,max_length=100)
    email: str = Field(min_length=3,max_length=254)
    password: str = Field(min_length=8,max_length=200)

    @field_validator('name')
    @classmethod
    def clean_name(cls,v):
        if not v.strip(): raise ValueError('Name cannot be blank')
        return v.strip()

    @field_validator('email')
    @classmethod
    def clean_email(cls,v):
        import re
        v=v.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',v): raise ValueError('Invalid email')
        return v
