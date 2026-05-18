import datetime
from typing import Any, Dict, Iterable, Optional

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .serialize import to_dict as _to_dict

playlist_track = sqlalchemy.Table(
    "playlist_track",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column("playlist_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("playlists.id"), primary_key=True),
    sqlalchemy.Column("track_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("tracks.id"), primary_key=True),
    sqlalchemy.Column("position", sqlalchemy.Integer, default=0),
)


class Playlist(SqlAlchemyBase):
    __tablename__ = "playlists"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_public = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)

    owner = orm.relationship("User", back_populates="playlists")
    tracks = orm.relationship("Track", secondary=playlist_track, back_populates="playlists")

    def to_dict(self, only: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        return _to_dict(self, only=only)

    def __repr__(self) -> str:
        return f"<Playlist {self.id} {self.name}>"
