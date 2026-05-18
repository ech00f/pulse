import datetime
from typing import Any, Dict, Iterable, Optional

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .serialize import to_dict as _to_dict


class Track(SqlAlchemyBase):
    __tablename__ = "tracks"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="Неизвестный")
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cover_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_public = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    uploader = orm.relationship("User", back_populates="tracks")
    favorites = orm.relationship("Favorite", back_populates="track")
    playlists = orm.relationship("Playlist", secondary="playlist_track", back_populates="tracks")

    def to_dict(self, only: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        return _to_dict(self, only=only)

    def __repr__(self) -> str:
        return f"<Track {self.id} {self.title}>"
