"""REST API для треков (JSON)."""

import flask
from flask import jsonify, make_response, request

from data import db_session
from data.tracks import Track
from validation.track_validator import validate_track_fields

blueprint = flask.Blueprint("tracks_api", __name__)


@blueprint.route("/api/tracks", methods=["GET"])
def list_tracks():
    db_sess = db_session.create_session()
    query = db_sess.query(Track).filter(Track.is_public.is_(True))
    search = request.args.get("q", "").strip()
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Track.title.ilike(pattern)) | (Track.artist.ilike(pattern))
        )
    tracks = query.order_by(Track.created_date.desc()).all()
    return jsonify(
        {
            "tracks": [
                item.to_dict(
                    only=(
                        "id",
                        "title",
                        "artist",
                        "filename",
                        "cover_filename",
                        "created_date",
                        "user_id",
                    )
                )
                for item in tracks
            ]
        }
    )


@blueprint.route("/api/tracks/<int:track_id>", methods=["GET"])
def get_track(track_id: int):
    db_sess = db_session.create_session()
    track = db_sess.get(Track, track_id)
    if not track or not track.is_public:
        return make_response(jsonify({"error": "Not found"}), 404)
    return jsonify(
        {
            "track": track.to_dict(
                only=(
                    "id",
                    "title",
                    "artist",
                    "filename",
                    "cover_filename",
                    "is_public",
                    "created_date",
                    "user_id",
                )
            )
        }
    )


@blueprint.route("/api/tracks", methods=["POST"])
def create_track():
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    required = ("title", "artist", "filename", "user_id")
    if not all(key in request.json for key in required):
        return make_response(jsonify({"error": "Bad request"}), 400)
    errors = validate_track_fields(
        request.json["title"],
        request.json["artist"],
        request.json["filename"],
    )
    if errors:
        return make_response(jsonify({"error": errors}), 400)
    db_sess = db_session.create_session()
    track = Track(
        title=request.json["title"],
        artist=request.json["artist"],
        filename=request.json["filename"],
        cover_filename=request.json.get("cover_filename"),
        user_id=request.json["user_id"],
        is_public=request.json.get("is_public", True),
    )
    db_sess.add(track)
    db_sess.commit()
    return jsonify({"id": track.id}), 201


@blueprint.route("/api/tracks/<int:track_id>", methods=["DELETE"])
def delete_track(track_id: int):
    db_sess = db_session.create_session()
    track = db_sess.get(Track, track_id)
    if not track:
        return make_response(jsonify({"error": "Not found"}), 404)
    db_sess.delete(track)
    db_sess.commit()
    return jsonify({"success": "OK"})
