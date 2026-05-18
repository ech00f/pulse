import io
import os

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

import config
from api import playlists_api, tracks_api, users_api
from data import db_session
from data.favorites import Favorite
from data.playlists import Playlist
from data.tracks import Track
from data.users import User
from forms.track import UploadTrackForm
from forms.user import LoginForm, RegisterForm
from routes.playlists_web import blueprint as playlists_web_bp
from services.export_csv import save_catalog_snapshot, tracks_to_csv
from utils import allowed_file, save_audio_file, save_cover_file
from validation.track_validator import validate_track_fields
from validation.user_validator import validate_registration

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(config.UPLOAD_FOLDER)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


def init_app():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    db_session.global_init(str(config.DB_PATH))
    app.register_blueprint(tracks_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(playlists_api.blueprint)
    app.register_blueprint(playlists_web_bp)
    catalog_path = config.BASE_DIR / "data" / "catalog_export.csv"
    save_catalog_snapshot(str(catalog_path))


@app.route("/")
def index():
    db_sess = db_session.create_session()
    search = request.args.get("q", "").strip()
    query = db_sess.query(Track).filter(Track.is_public.is_(True))
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Track.title.ilike(pattern)) | (Track.artist.ilike(pattern))
        )
    tracks = query.order_by(Track.created_date.desc()).all()
    public_playlists = (
        db_sess.query(Playlist)
        .filter(Playlist.is_public.is_(True))
        .order_by(Playlist.created_date.desc())
        .limit(6)
        .all()
    )
    return render_template(
        "index.html", tracks=tracks, search=search, public_playlists=public_playlists
    )


@app.route("/track/<int:track_id>")
def track_page(track_id: int):
    db_sess = db_session.create_session()
    track = db_sess.get(Track, track_id)
    if not track:
        abort(404)
    if not track.is_public and (
        not current_user.is_authenticated or track.user_id != current_user.id
    ):
        abort(403)
    in_favorites = False
    if current_user.is_authenticated:
        in_favorites = (
            db_sess.query(Favorite)
            .filter(Favorite.user_id == current_user.id, Favorite.track_id == track.id)
            .first()
            is not None
        )
    return render_template("track.html", track=track, in_favorites=in_favorites)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        reg_errors = validate_registration(
            form.name.data, form.email.data, form.password.data
        )
        if reg_errors:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="; ".join(reg_errors),
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пользователь с такой почтой уже есть",
            )
        user = User(name=form.name.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("index"))
        return render_template(
            "login.html",
            title="Вход",
            form=form,
            message="Неверная почта или пароль",
        )
    return render_template("login.html", title="Вход", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadTrackForm()
    if form.validate_on_submit():
        field_errors = validate_track_fields(
            form.title.data, form.artist.data, form.audio.data.filename
        )
        if field_errors:
            for err in field_errors:
                flash(err, "danger")
            return render_template("upload.html", form=form)
        if not allowed_file(form.audio.data.filename):
            flash("Недопустимый формат аудио", "danger")
            return render_template("upload.html", form=form)
        audio_name = save_audio_file(form.audio.data)
        cover_name = save_cover_file(form.cover.data)
        db_sess = db_session.create_session()
        track = Track(
            title=form.title.data.strip(),
            artist=form.artist.data.strip(),
            filename=audio_name,
            cover_filename=cover_name,
            is_public=form.is_public.data,
            user_id=current_user.id,
        )
        db_sess.add(track)
        db_sess.commit()
        save_catalog_snapshot(str(config.BASE_DIR / "data" / "catalog_export.csv"))
        flash("Трек загружен", "success")
        return redirect(url_for("track_page", track_id=track.id))
    return render_template("upload.html", form=form)


@app.route("/my")
@login_required
def my_tracks():
    db_sess = db_session.create_session()
    tracks = (
        db_sess.query(Track)
        .filter(Track.user_id == current_user.id)
        .order_by(Track.created_date.desc())
        .all()
    )
    return render_template("my_tracks.html", tracks=tracks)


@app.route("/favorites")
@login_required
def favorites():
    db_sess = db_session.create_session()
    rows = (
        db_sess.query(Track)
        .join(Favorite, Favorite.track_id == Track.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.id.desc())
        .all()
    )
    return render_template("favorites.html", tracks=rows)


@app.route("/favorite/<int:track_id>", methods=["POST"])
@login_required
def toggle_favorite(track_id: int):
    db_sess = db_session.create_session()
    track = db_sess.get(Track, track_id)
    if not track:
        abort(404)
    existing = (
        db_sess.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.track_id == track_id)
        .first()
    )
    if existing:
        db_sess.delete(existing)
    else:
        db_sess.add(Favorite(user_id=current_user.id, track_id=track_id))
    db_sess.commit()
    return redirect(request.referrer or url_for("track_page", track_id=track_id))


@app.route("/delete/<int:track_id>", methods=["POST"])
@login_required
def delete_track(track_id: int):
    db_sess = db_session.create_session()
    track = (
        db_sess.query(Track)
        .filter(Track.id == track_id, Track.user_id == current_user.id)
        .first()
    )
    if not track:
        abort(404)
    track.playlists.clear()
    _remove_track_files(track)
    db_sess.delete(track)
    db_sess.commit()
    save_catalog_snapshot(str(config.BASE_DIR / "data" / "catalog_export.csv"))
    flash("Трек удалён", "info")
    return redirect(url_for("my_tracks"))


def _remove_track_files(track: Track) -> None:
    audio = config.UPLOAD_FOLDER / "audio" / track.filename
    if audio.exists():
        audio.unlink()
    if track.cover_filename:
        cover = config.UPLOAD_FOLDER / "covers" / track.cover_filename
        if cover.exists():
            cover.unlink()


@app.route("/media/audio/<path:filename>")
def serve_audio(filename):
    directory = config.UPLOAD_FOLDER / "audio"
    return send_from_directory(directory, filename)


@app.route("/media/cover/<path:filename>")
def serve_cover(filename):
    directory = config.UPLOAD_FOLDER / "covers"
    return send_from_directory(directory, filename)


@app.route("/export/catalog.csv")
def export_catalog():
    output = io.StringIO(tracks_to_csv())
    return app.response_class(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=pulse_catalog.csv"},
    )


@app.route("/api/docs")
def api_docs():
    return render_template("api_docs.html")


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


init_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 22222))
    app.run(host="0.0.0.0", port=port, debug=True)
