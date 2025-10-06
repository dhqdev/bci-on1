"""Utility helpers to manage short boleto links.

This module provides a tiny file-backed URL shortener tailored for boleto links.
It stores mappings between generated short codes and original Servopa URLs so we
can share friendly links with clients.
"""

from __future__ import annotations

import json
import os
import threading
import time
import typing as t
from hashlib import blake2b

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SHORT_LINKS_FILE = os.path.join(DATA_DIR, "short_links.json")

_lock = threading.Lock()


def _ensure_storage() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SHORT_LINKS_FILE):
        with open(SHORT_LINKS_FILE, "w", encoding="utf-8") as fh:
            json.dump({}, fh)


def _load_links() -> dict:
    _ensure_storage()
    with open(SHORT_LINKS_FILE, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return {}


def _save_links(data: dict) -> None:
    _ensure_storage()
    with open(SHORT_LINKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _generate_code(url: str, salt: str | None = None, length: int = 8) -> str:
    hasher = blake2b(digest_size=16)
    hasher.update(url.encode("utf-8"))
    if salt:
        hasher.update(salt.encode("utf-8"))
    digest = hasher.hexdigest()
    return digest[:length]


def create_short_link(task_id: str | int, url: str) -> str:
    """Create (or reuse) a short code for the given task/url."""

    if not url:
        raise ValueError("URL obrigatória para gerar link curto")

    task_id = str(task_id)

    with _lock:
        data = _load_links()

        # Reuse existing mapping if the same task already points to this URL
        for code, meta in data.items():
            if meta.get("task_id") == task_id and meta.get("url") == url:
                return code

        # Otherwise, generate a new code; ensure uniqueness
        salt = str(time.time_ns())
        code = _generate_code(url, salt=salt)
        while code in data:
            salt = str(time.time_ns())
            code = _generate_code(url, salt=salt)

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        data[code] = {
            "task_id": task_id,
            "url": url,
            "created_at": timestamp,
            "updated_at": timestamp,
            "hits": 0,
        }

        _save_links(data)
        return code


def update_short_link(code: str, url: str) -> None:
    with _lock:
        data = _load_links()
        if code not in data:
            raise KeyError(f"Código curto '{code}' não encontrado")

        data[code]["url"] = url
        data[code]["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _save_links(data)


def resolve_short_link(code: str) -> t.Optional[str]:
    with _lock:
        data = _load_links()
        meta = data.get(code)
        if not meta:
            return None

        meta["hits"] = int(meta.get("hits", 0)) + 1
        meta["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _save_links(data)
        return meta.get("url")


def get_short_code_for_task(task_id: str | int) -> t.Optional[str]:
    task_id = str(task_id)
    with _lock:
        data = _load_links()
        for code, meta in data.items():
            if meta.get("task_id") == task_id:
                return code
    return None


def build_public_short_url(base_url: str, code: str) -> str:
    base_url = base_url.rstrip("/")
    return f"{base_url}/boleto/{code}"
