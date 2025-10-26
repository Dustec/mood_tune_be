from fastapi import HTTPException
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate
from app.services import encode_cursor, decode_cursor

MIN_TRACKS_TO_FINALIZE = 20


class PlaylistsService:
    @staticmethod
    def create(db: Session, data: PlaylistCreate) -> Playlist:
        pl = Playlist(
            user_id=data.user_id,
            seed_emotion=data.seed_emotion,
            strategy=data.strategy,
            title=data.title,
            description=data.description,
            provider=data.provider,
        )
        db.add(pl)
        db.commit()
        db.refresh(pl)
        return pl

    @staticmethod
    def list(db: Session, user_id: str | None, provider: str | None, limit: int, cursor: str | None) -> tuple[list[Playlist], str | None]:
        q = select(Playlist)
        filters = []

        if user_id:
            filters.append(Playlist.user_id == user_id)
        if provider:
            filters.append(Playlist.provider == provider)

        if filters:
            q = q.where(and_(*filters))

        # Paginación por cursor
        if cursor:
            try:
                created_at, last_id = decode_cursor(cursor)
                q = q.where(
                    or_(
                        Playlist.created_at < created_at,
                        and_(Playlist.created_at ==
                             created_at, Playlist.id < last_id)
                    )
                )
            except Exception:
                pass  # Ignorar cursor inválido

        q = q.order_by(desc(Playlist.created_at),
                       desc(Playlist.id)).limit(limit + 1)
        items = db.execute(q).scalars().all()

        next_cursor = None
        if len(items) > limit:
            items = items[:limit]
            last = items[-1]
            next_cursor = encode_cursor(last.created_at, last.id)

        return items, next_cursor

    @staticmethod
    def get(db: Session, pid: str) -> Playlist:
        pl = db.get(Playlist, pid)
        if not pl:
            raise HTTPException(status_code=404, detail="playlist_not_found")
        return pl

    @staticmethod
    def update(db: Session, pid: str, data: PlaylistUpdate) -> Playlist:
        pl = PlaylistsService.get(db, pid)
        # Campos no permitidos: user_id, provider
        for field in ("title", "description", "strategy"):
            val = getattr(data, field)
            if val is not None:
                setattr(pl, field, val)
        db.add(pl)
        db.commit()
        db.refresh(pl)
        return pl

    @staticmethod
    def delete(db: Session, pid: str) -> None:
        pl = PlaylistsService.get(db, pid)
        db.delete(pl)
        db.commit()

    @staticmethod
    def finalize(db: Session, pid: str, provider_playlist_id: str | None) -> Playlist:
        pl = PlaylistsService.get(db, pid)
        count = db.execute(select(PlaylistTrack).where(
            PlaylistTrack.playlist_id == pid)).scalars().all()
        if len(count) < MIN_TRACKS_TO_FINALIZE:
            raise HTTPException(
                status_code=422, detail="playlist_needs_>=20_tracks")
        if pl.provider_playlist_id:
            raise HTTPException(
                status_code=409, detail="provider_playlist_id_already_set")
        if provider_playlist_id:
            pl.provider_playlist_id = provider_playlist_id
        db.add(pl)
        db.commit()
        db.refresh(pl)
        return pl
