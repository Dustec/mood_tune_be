from sqlalchemy import CheckConstraint, Index, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


EMOTIONS = ("joy", "sadness", "anger", "fear",
            "disgust", "surprise", "neutral")
STRATEGIES = ("maintain", "change")
PROVIDERS = ("spotify",)


class Playlist(Base):
    __tablename__ = "playlists"

    # Usamos server_default para Postgres y onupdate para compatibilidad en pruebas (SQLite)
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")  # Alembic creará EXTENSION
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    seed_emotion: Mapped[str]
    strategy: Mapped[str]
    title: Mapped[str]
    description: Mapped[str | None]
    provider: Mapped[str]
    provider_playlist_id: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False)

    tracks = relationship(
        "PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            f"seed_emotion IN {EMOTIONS}", name="ck_playlists_seed_emotion"),
        CheckConstraint(f"strategy IN {STRATEGIES}",
                        name="ck_playlists_strategy"),
        CheckConstraint("provider = 'spotify'",
                        name="ck_playlists_provider"),
        # UNIQUE (provider, provider_playlist_id) cuando provider_playlist_id no es NULL se hará con índice parcial en migración
        Index("ix_playlists_user_created_at_desc",
              "user_id", text("created_at DESC")),
    )
