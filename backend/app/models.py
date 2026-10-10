from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def uid(): return str(uuid4())
def now(): return datetime.now(timezone.utc)

class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)

class POI(Base):
    __tablename__ = 'pois'
    __table_args__ = (CheckConstraint('latitude BETWEEN -90 AND 90'), CheckConstraint('longitude BETWEEN -180 AND 180'), CheckConstraint('radius BETWEEN 10 AND 500'))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(150))
    name_en: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(40), index=True)
    address: Mapped[str] = mapped_column(String(250))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    radius: Mapped[int] = mapped_column(Integer, default=30)
    source_url: Mapped[str] = mapped_column(Text, default='')
    published_version: Mapped[str | None] = mapped_column(ForeignKey('content_versions.id', use_alter=True, name='fk_poi_published_version'), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Content(Base):
    __tablename__ = 'content_versions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    poi_id: Mapped[str] = mapped_column(ForeignKey('pois.id'), index=True)
    vi: Mapped[str] = mapped_column(Text)
    en: Mapped[str] = mapped_column(Text, default='')
    zh: Mapped[str] = mapped_column(Text, default='', server_default='')
    fr: Mapped[str] = mapped_column(Text, default='', server_default='')
    ja: Mapped[str] = mapped_column(Text, default='', server_default='')
    state: Mapped[str] = mapped_column(String(24), default='DRAFT')
    source: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey('admins.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    poi_id: Mapped[str] = mapped_column(ForeignKey('pois.id'), index=True)
    source_url: Mapped[str] = mapped_column(Text)
    key: Mapped[str] = mapped_column(String(200), unique=True)
    state: Mapped[str] = mapped_column(String(24), default='PENDING', index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default='')
    content_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Consent(Base):
    __tablename__ = 'consents'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    policy: Mapped[str] = mapped_column(String(20), default='2026-01')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Event(Base):
    __tablename__ = 'analytics_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    consent_id: Mapped[str] = mapped_column(ForeignKey('consents.id'), index=True)
    poi_id: Mapped[str] = mapped_column(ForeignKey('pois.id'))
    kind: Mapped[str] = mapped_column(String(30))
    locale: Mapped[str] = mapped_column(String(5))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Audit(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admins.id'))
    action: Mapped[str] = mapped_column(String(50))
    target: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
