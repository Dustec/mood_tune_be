from typing import Annotated, Literal
from pydantic import BaseModel, Field


Order = Annotated[int, Field(gt=0, le=10000)]


class TrackBase(BaseModel):
    provider_track_id: str = Field(..., examples=["3n3Ppam7vgaVa1iaRUc9Lp"])
    title: str = Field(..., examples=["Mr. Brightside"])
    artist: str = Field(..., examples=["The Killers"])
    duration_ms: int | None = Field(None, ge=0)


class TrackCreate(TrackBase):
    pass


class TrackOut(TrackBase):
    track_order: Order


class TracksBulkIn(BaseModel):
    tracks: list[TrackCreate]


class TrackReorderItem(BaseModel):
    provider_track_id: str | None = None
    track_order: Order | None = None
    new_order: Order


class TrackReorderIn(BaseModel):
    __root__: list[TrackReorderItem]

    def items(self) -> list[TrackReorderItem]:
        return self.__root__