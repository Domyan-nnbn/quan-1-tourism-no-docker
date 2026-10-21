from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
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
    geofence_type: Literal['circle','polygon'] = 'circle'
    polygon_coordinates: list[tuple[float,float]] | None = Field(default=None, max_length=50)
    exit_buffer_m: int = Field(default=20, ge=5, le=100)
    dwell_seconds: int = Field(default=10, ge=1, le=60)
    gps_accuracy_threshold_m: int = Field(default=25, ge=5, le=50)

    @model_validator(mode='after')
    def validate_geofence(self):
        points = self.polygon_coordinates
        if self.geofence_type == 'polygon':
            if points is None or not 3 <= len(points) <= 50:
                raise ValueError('Polygon requires 3 to 50 vertices')
            if len(set(points)) < 3:
                raise ValueError('Polygon vertices must be distinct')
            if any(not (-90 <= lat <= 90 and -180 <= lon <= 180) for lat,lon in points):
                raise ValueError('Invalid polygon coordinates')
            # Reject degenerate/self-intersecting polygons and overly large shapes.
            from math import cos, radians
            lat0 = sum(v[0] for v in points)/len(points)
            xy = [((lon-self.longitude)*111320*cos(radians(lat0)), (lat-self.latitude)*111320) for lat,lon in points]
            area = abs(sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy))))/2
            if area < 25 or max(max(abs(x),abs(y)) for x,y in xy)>1000:
                raise ValueError('Polygon area too small or more than 1 km from POI')
            def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            for i in range(len(xy)):
                for j in range(i+1,len(xy)):
                    if (i-j)%len(xy) in (0,1,len(xy)-1):continue
                    a,b,c,d=xy[i],xy[(i+1)%len(xy)],xy[j],xy[(j+1)%len(xy)]
                    if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:
                        raise ValueError('Polygon edges must not intersect')
        else:
            self.polygon_coordinates = None
        return self
    source_url: str = Field(default='', max_length=1000)
    image_url: str = Field(default='', max_length=2000)
    opening_hours: str = Field(default='', max_length=1000)

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

    @field_validator('image_url')
    @classmethod
    def safe_image_url(cls, v):
        if not v: return v
        u = urlsplit(v)
        if u.scheme not in ('https', 'http') or not u.netloc:
            raise ValueError('Image URL must use http(s)')
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
    kind: Literal['narration_started','narration_completed','narration_error']
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

class ChangePassword(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)

class DeleteAccount(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)

class UserLockInput(BaseModel):
    locked: bool

class AdminSettingsInput(BaseModel):
    default_language: Literal['vi','en'] = 'vi'
    gps_accuracy_m: int = Field(default=25, ge=5, le=25)
    activation_dwell_seconds: int = Field(default=3, ge=1, le=30)
    repeat_cooldown_minutes: int = Field(default=5, ge=1, le=120)
