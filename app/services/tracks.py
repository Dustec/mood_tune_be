from fastapi import HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.schemas.playlist_track import TracksBulkIn, TrackReorderIn


class TracksService:
    @staticmethod
    def bulk_add(db: Session, pid: str, data: TracksBulkIn) -> tuple[list[PlaylistTrack], int]:
        TracksService._assert_playlist(db, pid)

        # Obtener el siguiente order
        max_order = db.scalar(select(func.max(PlaylistTrack.track_order)).where(
            PlaylistTrack.playlist_id == pid))
        next_order = (max_order or 0) + 1

        inserted = []
        skipped = 0

        for t in data.tracks:
            # Verificar duplicados
            existing = db.scalar(
                select(PlaylistTrack).where(
                    PlaylistTrack.playlist_id == pid,
                    PlaylistTrack.provider_track_id == t.provider_track_id
                )
            )

            if existing:
                skipped += 1
                continue

            row = PlaylistTrack(
                playlist_id=pid,
                track_order=next_order,
                provider_track_id=t.provider_track_id,
                title=t.title,
                artist=t.artist,
                duration_ms=t.duration_ms,
            )
            db.add(row)
            inserted.append(row)
            next_order += 1

        db.commit()
        # refrescar para orders
        for r in inserted:
            db.refresh(r)

        return inserted, skipped

    @staticmethod
    def reorder(db: Session, pid: str, items: TrackReorderIn):
        TracksService._assert_playlist(db, pid)
        # Resolver mapping (current -> new)
        mapping: dict[int, int] = {}

        for it in items.items():
            if it.provider_track_id is None and it.track_order is None:
                raise HTTPException(
                    status_code=422, detail="each_item_requires_provider_track_id_or_track_order")

            # Encontrar current_order
            if it.track_order is not None:
                current = it.track_order
            else:
                current = db.scalar(
                    select(PlaylistTrack.track_order).where(
                        PlaylistTrack.playlist_id == pid,
                        PlaylistTrack.provider_track_id == it.provider_track_id,
                    )
                )

            if current is None:
                raise HTTPException(
                    status_code=404, detail=f"track_not_found:{it.provider_track_id}")

            mapping[current] = it.new_order

        # Validar no repetidos en new_order
        new_orders = list(mapping.values())
        if len(new_orders) != len(set(new_orders)):
            raise HTTPException(
                status_code=422, detail="duplicate_new_order_values")

        # Transaccional: reordenar usando desplazamiento temporal para evitar colisiones
        OFFSET = 100000
        try:
            for cur, new in mapping.items():
                db.execute(
                    update(PlaylistTrack)
                    .where(PlaylistTrack.playlist_id == pid, PlaylistTrack.track_order == cur)
                    .values(track_order=new + OFFSET)
                )

            for cur, new in mapping.items():
                db.execute(
                    update(PlaylistTrack)
                    .where(PlaylistTrack.playlist_id == pid, PlaylistTrack.track_order == new + OFFSET)
                    .values(track_order=new)
                )

            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=422, detail="reorder_failed")

    @staticmethod
    def delete_by_order(db: Session, pid: str, order: int):
        TracksService._assert_playlist(db, pid)
        row = db.get(PlaylistTrack, {"playlist_id": pid, "track_order": order})
        if not row:
            raise HTTPException(status_code=404, detail="track_not_found")
        db.delete(row)
        db.commit()

    @staticmethod
    def _assert_playlist(db: Session, pid: str) -> None:
        """Verifica que la playlist existe."""
        pl = db.get(Playlist, pid)
        if not pl:
            raise HTTPException(status_code=404, detail="playlist_not_found")
