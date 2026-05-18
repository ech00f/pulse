"""REST API плейлистов."""

import flask
from flask import jsonify, make_response, request

from data import db_session
from data.playlists import Playlist
from data.tracks import Track

blueprint = flask.Blueprint("playlists_api", __name__)


def _playlist_payload(playlist: Playlist, with_tracks: bool = False) -> dict:
    data = playlist.to_dict(only=("id", "name", "is_public", "user_id", "created_date"))
    if with_tracks:
        data["tracks"] = [
            track.to_dict(only=("id", "title", "artist", "filename", "cover_filename"))
            for track in playlist.tracks
        ]
    else:
        data["tracks_count"] = len(playlist.tracks)
    return data


@blueprint.route("/api/playlists", methods=["GET"])
def list_playlists():
    db_sess = db_session.create_session()
    query = db_sess.query(Playlist).filter(Playlist.is_public.is_(True))
    user_id = request.args.get("user_id", type=int)
    if user_id is not None:
        query = db_sess.query(Playlist).filter(Playlist.user_id == user_id)
    playlists = query.order_by(Playlist.created_date.desc()).all()
    return jsonify({"playlists": [_playlist_payload(pl) for pl in playlists]})


@blueprint.route("/api/playlists/<int:playlist_id>", methods=["GET"])
def get_playlist(playlist_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.get(Playlist, playlist_id)
    if not playlist or not playlist.is_public:
        return make_response(jsonify({"error": "Not found"}), 404)
    return jsonify({"playlist": _playlist_payload(playlist, with_tracks=True)})


@blueprint.route("/api/playlists", methods=["POST"])
def create_playlist():
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    name = (request.json.get("name") or "").strip()
    user_id = request.json.get("user_id")
    if not name or user_id is None:
        return make_response(jsonify({"error": "Bad request"}), 400)
    db_sess = db_session.create_session()
    playlist = Playlist(
        name=name,
        user_id=user_id,
        is_public=request.json.get("is_public", True),
    )
    db_sess.add(playlist)
    db_sess.commit()
    return jsonify({"id": playlist.id}), 201


@blueprint.route("/api/playlists/<int:playlist_id>/tracks", methods=["POST"])
def add_track_to_playlist(playlist_id: int):
    if not request.json or "track_id" not in request.json:
        return make_response(jsonify({"error": "Bad request"}), 400)
    db_sess = db_session.create_session()
    playlist = db_sess.get(Playlist, playlist_id)
    track = db_sess.get(Track, request.json["track_id"])
    if not playlist or not track:
        return make_response(jsonify({"error": "Not found"}), 404)
    if track not in playlist.tracks:
        playlist.tracks.append(track)
        db_sess.commit()
    return jsonify({"success": "OK"})


@blueprint.route("/api/playlists/<int:playlist_id>/tracks/<int:track_id>", methods=["DELETE"])
def remove_track_from_playlist(playlist_id: int, track_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.get(Playlist, playlist_id)
    track = db_sess.get(Track, track_id)
    if not playlist or not track:
        return make_response(jsonify({"error": "Not found"}), 404)
    if track in playlist.tracks:
        playlist.tracks.remove(track)
        db_sess.commit()
    return jsonify({"success": "OK"})
