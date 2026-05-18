"""Веб-страницы плейлистов."""

import flask
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from data import db_session
from data.playlists import Playlist
from data.tracks import Track
from forms.playlist import PlaylistForm

blueprint = flask.Blueprint("playlists_web", __name__)


def _can_view(playlist: Playlist) -> bool:
    if playlist.is_public:
        return True
    return current_user.is_authenticated and playlist.user_id == current_user.id


@blueprint.route("/playlists")
@login_required
def my_playlists():
    db_sess = db_session.create_session()
    playlists = (
        db_sess.query(Playlist)
        .filter(Playlist.user_id == current_user.id)
        .order_by(Playlist.created_date.desc())
        .all()
    )
    return render_template("playlists.html", playlists=playlists)


@blueprint.route("/playlists/create", methods=["GET", "POST"])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        playlist = Playlist(
            name=form.name.data.strip(),
            is_public=form.is_public.data,
            user_id=current_user.id,
        )
        db_sess.add(playlist)
        db_sess.commit()
        flash("Плейлист создан", "success")
        return redirect(url_for("playlists_web.playlist_detail", playlist_id=playlist.id))
    return render_template("playlist_form.html", form=form, title="Новый плейлист")


@blueprint.route("/playlists/<int:playlist_id>")
def playlist_detail(playlist_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.get(Playlist, playlist_id)
    if not playlist or not _can_view(playlist):
        abort(404)
    is_owner = current_user.is_authenticated and playlist.user_id == current_user.id
    my_tracks = []
    if is_owner:
        my_tracks = (
            db_sess.query(Track)
            .filter(Track.user_id == current_user.id)
            .order_by(Track.title)
            .all()
        )
    return render_template(
        "playlist_detail.html",
        playlist=playlist,
        is_owner=is_owner,
        my_tracks=my_tracks,
    )


@blueprint.route("/playlists/<int:playlist_id>/add/<int:track_id>", methods=["POST"])
@login_required
def add_track(playlist_id: int, track_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.query(Playlist).filter(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    ).first()
    track = db_sess.get(Track, track_id)
    if not playlist or not track or track.user_id != current_user.id:
        abort(404)
    if track not in playlist.tracks:
        playlist.tracks.append(track)
        db_sess.commit()
        flash("Трек добавлен в плейлист", "success")
    return redirect(url_for("playlists_web.playlist_detail", playlist_id=playlist_id))


@blueprint.route("/playlists/<int:playlist_id>/remove/<int:track_id>", methods=["POST"])
@login_required
def remove_track(playlist_id: int, track_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.query(Playlist).filter(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    ).first()
    track = db_sess.get(Track, track_id)
    if not playlist or not track:
        abort(404)
    if track in playlist.tracks:
        playlist.tracks.remove(track)
        db_sess.commit()
    return redirect(url_for("playlists_web.playlist_detail", playlist_id=playlist_id))


@blueprint.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
@login_required
def delete_playlist(playlist_id: int):
    db_sess = db_session.create_session()
    playlist = db_sess.query(Playlist).filter(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    ).first()
    if not playlist:
        abort(404)
    db_sess.delete(playlist)
    db_sess.commit()
    flash("Плейлист удалён", "info")
    return redirect(url_for("playlists_web.my_playlists"))
