"""Проверка данных пользователя."""

import re
from typing import List

UserValidationError = ValueError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NAME_MAX = 100


def validate_registration(name: str, email: str, password: str) -> List[str]:
    errors: List[str] = []
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name:
        errors.append("Укажите имя.")
    elif len(name) > _NAME_MAX:
        errors.append(f"Имя не длиннее {_NAME_MAX} символов.")

    if not email:
        errors.append("Укажите почту.")
    elif not _EMAIL_RE.match(email):
        errors.append("Некорректный адрес почты.")

    if not password:
        errors.append("Укажите пароль.")
    elif len(password) < 4:
        errors.append("Пароль не короче 4 символов.")

    return errors
