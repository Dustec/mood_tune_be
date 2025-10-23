from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey(
        "playlists.id", ondelete="CASCADE"), primary_key=True)
    track_order: Mapped[int] = mapped_column(primary_key=True)
    provider_track_id: Mapped[str]
    title: Mapped[str]
    artist: Mapped[str]
    duration_ms: Mapped[int | None]

    playlist = relationship(
        "app.models.playlist.Playlist", back_populates="tracks")

    __table_args__ = (
        CheckConstraint("track_order > 0", name="ck_tracks_order_pos"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0",
                        name="ck_tracks_duration_nonneg"),
        UniqueConstraint("playlist_id", "provider_track_id",
                         name="uq_tracks_playlist_provider_track"),
        Index("ix_tracks_playlist_id", "playlist_id"),
    )
