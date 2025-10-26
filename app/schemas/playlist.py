from typing import Annotated, Literal
from pydantic import BaseModel, Field
from app.schemas.playlist_track import TrackOut

Emotion = Literal["joy", "sadness", "anger",
                  "fear", "disgust", "surprise", "neutral"]
Strategy = Literal["maintain", "change"]
Provider = Literal["spotify"]


class PlaylistCreate(BaseModel):
    user_id: str = Field(..., examples=[
                         "1f2b1c4e-1d2a-4f44-9f8b-9b9b9b9b9b9b"])
    seed_emotion: Emotion
    strategy: Strategy
    title: str
    description: str | None = None
    provider: Provider


class PlaylistUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    strategy: Strategy | None = None


class PlaylistOut(BaseModel):
    id: str
    user_id: str
    seed_emotion: Emotion
    strategy: Strategy
    title: str
    description: str | None
    provider: Provider
    provider_playlist_id: str | None
    created_at: str
    updated_at: str


class PlaylistWithTracksOut(PlaylistOut):
    tracks: list[TrackOut]


class PlaylistsListOut(BaseModel):
    items: list[PlaylistOut]
    next_cursor: str | None
