from fastapi import APIRouter, Depends, Query, Body
def create_playlist(data: PlaylistCreate, db: Session = Depends(get_session)):
pl = PlaylistsService.create(db, data)
return pl.__dict__


@router.get("", response_model=PlaylistsListOut)
def list_playlists(
user_id: str | None = None,
provider: str | None = None,
limit: int = Query(20, ge=1, le=100),
cursor: str | None = None,
db: Session = Depends(get_session),
):
items, next_cursor = PlaylistsService.list(db, user_id, provider, limit, cursor)
return {
"items": [i.__dict__ for i in items],
"next_cursor": next_cursor,
}


@router.get("/{pid}", response_model=PlaylistWithTracksOut)
def get_playlist(pid: str, db: Session = Depends(get_session)):
pl = PlaylistsService.get(db, pid)
tracks = sorted(pl.tracks, key=lambda t: t.track_order)
d = pl.__dict__.copy()
d["tracks"] = [
{
"track_order": t.track_order,
"provider_track_id": t.provider_track_id,
"title": t.title,
"artist": t.artist,
"duration_ms": t.duration_ms,
}
for t in tracks
]
return d


@router.put("/{pid}", response_model=PlaylistOut)
def update_playlist(pid: str, data: PlaylistUpdate, db: Session = Depends(get_session)):
pl = PlaylistsService.update(db, pid, data)
return pl.__dict__


@router.delete("/{pid}", status_code=204)
def delete_playlist(pid: str, db: Session = Depends(get_session)):
PlaylistsService.delete(db, pid)
return


@router.post("/{pid}/finalize", response_model=PlaylistOut)
def finalize_playlist(
pid: str,
body: dict | None = Body(default=None, examples=[{"provider_playlist_id": "37i9dQZF1DXcBWIGoYBM5M"}]),
db: Session = Depends(get_session),
):
provider_playlist_id = (body or {}).get("provider_playlist_id")
pl = PlaylistsService.finalize(db, pid, provider_playlist_id)
return pl.__dict__


@router.post("/{pid}/tracks:bulkAdd", status_code=201)
def bulk_add_tracks(pid: str, data: TracksBulkIn, db: Session = Depends(get_session)):
inserted, skipped = TracksService.bulk_add(db, pid, data)
return {
"inserted": [
{
"track_order": t.track_order,
"provider_track_id": t.provider_track_id,
"title": t.title,
"artist": t.artist,
"duration_ms": t.duration_ms,
}
for t in inserted
],
"skipped_duplicates": skipped,
}