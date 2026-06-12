from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    Enum as SqlEnum,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


# =====================================================
# BASE
# =====================================================

class Base(DeclarativeBase):
    pass


# =====================================================
# MIXINS
# =====================================================

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# =====================================================
# ENUMS
# =====================================================

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class ContentType(str, Enum):
    POST = "post"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SCHEDULED = "scheduled"
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"


class PlatformType(str, Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


# =====================================================
# MEDIA ASSETS
# =====================================================

class MediaAsset(Base, TimestampMixin):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    media_type: Mapped[MediaType] = mapped_column(
        SqlEnum(MediaType)
    )

    original_url: Mapped[str] = mapped_column(
        Text
    )

    storage_url: Mapped[str] = mapped_column(
        Text
    )

    filename: Mapped[str] = mapped_column(
        String(500)
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    alt_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    posted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    contents: Mapped[list["Content"]] = relationship(
        back_populates="media_asset"
    )

# =====================================================
# IMAGES_GOD
# =====================================================
class Images_God(Base):
    __tablename__ = "images_god"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255))
    gcp_bucket_url: Mapped[str] = mapped_column(String(255))    
    gcp_filename: Mapped[str] = mapped_column(String(255))
    prompt_used: Mapped[str] = mapped_column(String(255))
    model_used: Mapped[str] = mapped_column(String(255))
    insta_url: Mapped[str] = mapped_column(String(255))
    yt_url: Mapped[str] = mapped_column(String(255))
    alt_text: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    yt_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    insta_posted: Mapped[bool] = mapped_column(Boolean, default=False)   
    description: Mapped[str] = mapped_column(String(255))
    posted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =====================================================
# VIDEO_GOD
# =====================================================
class Video_God(Base):
    __tablename__ = "videos_god"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255))
    gcp_bucket_url: Mapped[str] = mapped_column(String(255))    
    gcp_filename: Mapped[str] = mapped_column(String(255))
    prompt_used: Mapped[str] = mapped_column(String(255))
    model_used: Mapped[str] = mapped_column(String(255))
    insta_url: Mapped[str] = mapped_column(String(255))
    yt_url: Mapped[str] = mapped_column(String(255))
    alt_text: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    yt_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    insta_posted: Mapped[bool] = mapped_column(Boolean, default=False)      
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ! on demand
class videos_on_demand(Base):
    __tablename__ = "videos_on_demand"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt: Mapped[str] = mapped_column(String(255))
    yt_post: Mapped[bool] = mapped_column(Boolean, default=False)
    generated : Mapped[bool] = mapped_column(Boolean,default=False)
    insta_post: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class images_on_demand(Base):
    __tablename__ = "images_on_demand"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt: Mapped[str] = mapped_column(String(255))
    yt_post: Mapped[bool] = mapped_column(Boolean, default=False)
    generated : Mapped[bool] = mapped_column(Boolean,default=False)
    insta_post: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =====================================================
# CONTENT
# =====================================================

class Content(Base, TimestampMixin):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    content_type: Mapped[ContentType] = mapped_column(
        SqlEnum(ContentType)
    )

    caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hashtags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[ContentStatus] = mapped_column(
        SqlEnum(ContentStatus),
        default=ContentStatus.DRAFT,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    media_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_assets.id"),
        nullable=True,
    )

    media_asset: Mapped["MediaAsset"] = relationship(
        back_populates="contents"
    )

    publish_jobs: Mapped[list["PublishJob"]] = relationship(
        back_populates="content",
        cascade="all, delete-orphan",
    )

    analytics: Mapped[list["Analytics"]] = relationship(
        back_populates="content",
        cascade="all, delete-orphan",
    )


# =====================================================
# PUBLISH JOBS
# =====================================================

class PublishJob(Base, TimestampMixin):
    __tablename__ = "publish_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE")
    )

    platform: Mapped[PlatformType] = mapped_column(
        SqlEnum(PlatformType)
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    platform_post_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    content: Mapped["Content"] = relationship(
        back_populates="publish_jobs"
    )


# =====================================================
# ANALYTICS
# =====================================================

class Analytics(Base):
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE")
    )

    impressions: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    reach: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    comments: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    shares: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    saves: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    content: Mapped["Content"] = relationship(
        back_populates="analytics"
    )