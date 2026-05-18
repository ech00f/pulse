import uuid
from pathlib import Path
from typing import Optional

from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_audio_file(file_storage) -> str:
    """Сохраняет аудиофайл в static/uploads/audio, возвращает имя файла."""
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    folder = UPLOAD_FOLDER / "audio"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    file_storage.save(path)
    return name


def save_cover_file(file_storage) -> Optional[str]:
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp", "gif"}:
        return None
    name = f"{uuid.uuid4().hex}.{ext}"
    folder = UPLOAD_FOLDER / "covers"
    folder.mkdir(parents=True, exist_ok=True)
    file_storage.save(folder / name)
    return name


def track_audio_path(filename: str) -> Path:
    return UPLOAD_FOLDER / "audio" / filename


def track_cover_path(filename: Optional[str]) -> Optional[Path]:
    if not filename:
        return None
    return UPLOAD_FOLDER / "covers" / filename
