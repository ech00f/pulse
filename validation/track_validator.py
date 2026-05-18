"""Проверка полей трека при загрузке и в API."""

import re
from typing import List

from config import ALLOWED_EXTENSIONS

TrackValidationError = ValueError

_TITLE_MAX = 200
_ARTIST_MAX = 200
_BAD_CHARS = re.compile(r"[<>\"']")


def validate_track_fields(title: str, artist: str, audio_filename: str) -> List[str]:
    errors: List[str] = []
    title = (title or "").strip()
    artist = (artist or "").strip()

    if not title:
        errors.append("Укажите название трека.")
    elif len(title) > _TITLE_MAX:
        errors.append(f"Название не длиннее {_TITLE_MAX} символов.")
    elif _BAD_CHARS.search(title):
        errors.append("Название содержит недопустимые символы.")

    if not artist:
        errors.append("Укажите исполнителя.")
    elif len(artist) > _ARTIST_MAX:
        errors.append(f"Имя исполнителя не длиннее {_ARTIST_MAX} символов.")
    elif _BAD_CHARS.search(artist):
        errors.append("Имя исполнителя содержит недопустимые символы.")

    if not audio_filename or "." not in audio_filename:
        errors.append("Некорректное имя аудиофайла.")
    else:
        ext = audio_filename.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"Допустимые форматы: {', '.join(sorted(ALLOWED_EXTENSIONS))}.")

    return errors


def validate_track_fields_strict(title: str, artist: str, audio_filename: str) -> None:
    errors = validate_track_fields(title, artist, audio_filename)
    if errors:
        raise TrackValidationError("; ".join(errors))
