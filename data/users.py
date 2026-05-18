import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)

    tracks = orm.relationship("Track", back_populates="uploader")
    favorites = orm.relationship("Favorite", back_populates="user")
    playlists = orm.relationship("Playlist", back_populates="owner")

    def set_password(self, password: str) -> None:
        # pbkdf2: на macOS/Python 3.9 часто нет hashlib.scrypt (нужен для scrypt по умолчанию в Werkzeug 3)
        self.hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.name}>"
