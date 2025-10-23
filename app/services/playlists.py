from sqlalchemy import select, and_, or_, desc
items = db.execute(q).scalars().all()


next_cursor = None
if len(items) == limit:
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
count = db.scalar(select(PlaylistTrack).where(PlaylistTrack.playlist_id == pid).count())
if count is None:
count = db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == pid)).scalars().count()
# Fallback universal
count = db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == pid)).scalars().all()
if len(count) < MIN_TRACKS_TO_FINALIZE:
raise HTTPException(status_code=422, detail="playlist_needs_>=20_tracks")
if pl.provider_playlist_id:
raise HTTPException(status_code=409, detail="provider_playlist_id_already_set")
if provider_playlist_id:
pl.provider_playlist_id = provider_playlist_id
db.add(pl)
db.commit()
db.refresh(pl)
return pl