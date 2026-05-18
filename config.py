import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = os.environ.get("SECRET_KEY", "pulse_dev_secret_change_in_production")
DB_PATH = BASE_DIR / "db" / "pulse.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"mp3", "ogg", "wav", "m4a"}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB

# Публичный URL сайта (для Алисы и внешних ссылок на треки)
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://127.0.0.1:2222")
