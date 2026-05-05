import base64
import os
import sqlite3
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SECRET_NAMES = (
    'html_comment',
    'sourcemap',
    'localstorage_admin',
    'debug_api',
    'idor',
    'sqli',
    'bonus',
)

KDF_ITERATIONS = 390000


def _derive_key(password, salt):
    if not password:
        raise ImproperlyConfigured('CTF_FLAG_DB_PASSWORD is required.')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))


def _fernet(password, salt):
    return Fernet(_derive_key(password, salt))


def _configured_db_path():
    raw_path = Path(settings.CTF_FLAG_DB_PATH)
    if raw_path.is_absolute():
        return raw_path
    return settings.BASE_DIR / raw_path


def _configured_password():
    return os.environ.get('CTF_FLAG_DB_PASSWORD', '')


def _connect(db_path):
    return sqlite3.connect(str(db_path))


def _ensure_schema(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS secrets (
            name TEXT PRIMARY KEY,
            salt BLOB NOT NULL,
            token BLOB NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )


def write_encrypted_flag_db(db_path, password, flags):
    missing = sorted(set(SECRET_NAMES) - set(flags))
    if missing:
        raise ValueError(f'Missing flag values: {", ".join(missing)}')

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    with _connect(db_path) as connection:
        _ensure_schema(connection)
        for name in SECRET_NAMES:
            salt = os.urandom(16)
            token = _fernet(password, salt).encrypt(str(flags[name]).encode('utf-8'))
            connection.execute(
                """
                INSERT INTO secrets(name, salt, token, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    salt = excluded.salt,
                    token = excluded.token,
                    updated_at = excluded.updated_at
                """,
                (name, salt, token, now),
            )


def load_encrypted_flags(db_path, password):
    db_path = Path(db_path)
    if not db_path.exists():
        raise ImproperlyConfigured(f'Encrypted CTF flag DB not found: {db_path}')

    try:
        with _connect(db_path) as connection:
            rows = connection.execute(
                'SELECT name, salt, token FROM secrets'
            ).fetchall()
    except sqlite3.DatabaseError as exc:
        raise ImproperlyConfigured('Encrypted CTF flag DB is not readable.') from exc

    flags = {}
    for name, salt, token in rows:
        try:
            flags[name] = _fernet(password, salt).decrypt(token).decode('utf-8')
        except InvalidToken as exc:
            raise ImproperlyConfigured('Encrypted CTF flag DB password is invalid.') from exc

    missing = sorted(set(SECRET_NAMES) - set(flags))
    if missing:
        raise ImproperlyConfigured(
            f'Encrypted CTF flag DB is missing values: {", ".join(missing)}'
        )
    return {name: flags[name] for name in SECRET_NAMES}


@lru_cache(maxsize=1)
def get_all_flags():
    return load_encrypted_flags(_configured_db_path(), _configured_password())


def clear_flag_cache():
    get_all_flags.cache_clear()


def get_flag(name):
    if name not in SECRET_NAMES:
        raise KeyError(name)
    return get_all_flags()[name]
