from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.db.session import get_session
from app.schemas.playlist_track import TrackReorderIn
from app.services.tracks import TracksService


router = APIRouter(prefix="/playlists/{pid}/tracks", tags=["tracks"])


@router.put("/reorder")
def reorder_tracks(pid: str, data: TrackReorderIn, db: Session = Depends(get_session)):
TracksService.reorder(db, pid, data)
return {"status": "ok"}


@router.delete("/{track_order}", status_code=204)
def delete_track(pid: str, track_order: int, db: Session = Depends(get_session)):
TracksService.delete_by_order(db, pid, track_order)
return