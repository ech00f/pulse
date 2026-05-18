"""Преобразование ORM-моделей в словарь для JSON (без сторонних библиотек)."""

import datetime
from typing import Any, Dict, Iterable, Optional


def to_dict(instance, only: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    if only is None:
        names = [column.name for column in instance.__table__.columns]
    else:
        names = list(only)
    result: Dict[str, Any] = {}
    for name in names:
        if "." in name:
            obj, attr = name.split(".", 1)
            value = getattr(getattr(instance, obj), attr)
        else:
            value = getattr(instance, name)
        if isinstance(value, datetime.datetime):
            value = value.isoformat()
        result[name.replace(".", "_")] = value
    return result
