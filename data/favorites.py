import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Favorite(SqlAlchemyBase):
    __tablename__ = "favorites"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    track_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tracks.id"), nullable=False)

    user = orm.relationship("User", back_populates="favorites")
    track = orm.relationship("Track", back_populates="favorites")

    __table_args__ = (sqlalchemy.UniqueConstraint("user_id", "track_id", name="uq_user_track"),)
