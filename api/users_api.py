"""REST API пользователей (без паролей)."""

import flask
from flask import jsonify, make_response

from data import db_session
from data.tracks import Track
from data.users import User

blueprint = flask.Blueprint("users_api", __name__)


def _public_user_dict(user: User) -> dict:
    db_sess = db_session.create_session()
    public_tracks = (
        db_sess.query(Track)
        .filter(Track.user_id == user.id, Track.is_public.is_(True))
        .count()
    )
    return {
        "id": user.id,
        "name": user.name,
        "created_date": user.created_date.isoformat() if user.created_date else None,
        "public_tracks_count": public_tracks,
    }


@blueprint.route("/api/users", methods=["GET"])
def list_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).order_by(User.id).all()
    return jsonify({"users": [_public_user_dict(user) for user in users]})


@blueprint.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        return make_response(jsonify({"error": "Not found"}), 404)
    tracks = (
        db_sess.query(Track)
        .filter(Track.user_id == user.id, Track.is_public.is_(True))
        .order_by(Track.created_date.desc())
        .all()
    )
    payload = _public_user_dict(user)
    payload["public_tracks"] = [
        track.to_dict(only=("id", "title", "artist", "cover_filename"))
        for track in tracks
    ]
    return jsonify({"user": payload})
