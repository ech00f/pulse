"""Проверка REST API (сервер: python main.py)."""

from requests import delete, get, post

BASE = "http://127.0.0.1:22222"


def main():
    print("tracks:", get(f"{BASE}/api/tracks").json())
    print("users:", get(f"{BASE}/api/users").json())
    print("playlists:", get(f"{BASE}/api/playlists").json())


if __name__ == "__main__":
    main()
