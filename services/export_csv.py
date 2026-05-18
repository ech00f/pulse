"""Экспорт каталога треков в CSV (доп. хранение данных)."""

import csv
import io
from datetime import datetime

from data import db_session
from data.tracks import Track


def tracks_to_csv() -> str:
  db_sess = db_session.create_session()
  tracks = db_sess.query(Track).filter(Track.is_public.is_(True)).all()
  buffer = io.StringIO()
  writer = csv.writer(buffer)
  writer.writerow(["id", "title", "artist", "filename", "user_id", "created_date"])
  for track in tracks:
    writer.writerow(
      [
        track.id,
        track.title,
        track.artist,
        track.filename,
        track.user_id,
        track.created_date.isoformat() if track.created_date else "",
      ]
    )
  return buffer.getvalue()


def save_catalog_snapshot(path: str) -> None:
  content = tracks_to_csv()
  with open(path, "w", encoding="utf-8", newline="") as file:
    file.write(content)
  _ = datetime.utcnow()
