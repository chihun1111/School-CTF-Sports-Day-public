import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from django.core.exceptions import ImproperlyConfigured


BONUS_TOKEN_TTL_SECONDS = 60 * 60
BONUS_TOKEN_MAX_LENGTH = 4096


@dataclass(frozen=True)
class BonusTokenResult:
    valid: bool
    winner: bool
    reason: str
    claims: dict


def _token_key():
    key = os.environ.get('CTF_BONUS_TOKEN_KEY', '')
    if not key:
        raise ImproperlyConfigured('CTF_BONUS_TOKEN_KEY is required.')
    return key.encode('utf-8')


def _encode_payload(payload):
    return base64.urlsafe_b64encode(payload).decode('ascii').rstrip('=')


def _decode_payload(payload_segment):
    payload_segment += '=' * (-len(payload_segment) % 4)
    return base64.urlsafe_b64decode(payload_segment.encode('ascii'))


def _sign_payload(payload):
    # Intentionally vulnerable for the final CTF challenge: this is a prefix MAC,
    # not HMAC, so it is length-extension vulnerable.
    return hashlib.sha256(_token_key() + payload).hexdigest()


def issue_guest_token(now=None):
    now = int(now or time.time())
    payload = (
        f'uid=student01&scope=sports-day&expires={now + BONUS_TOKEN_TTL_SECONDS}'
        '&role=guest'
    ).encode('ascii')
    return f'{_encode_payload(payload)}.{_sign_payload(payload)}'


def decode_token_payload(token):
    payload_segment, _digest = token.split('.', 1)
    return _decode_payload(payload_segment)


def _parse_claims(payload):
    claims = {}
    decoded = payload.decode('latin-1')
    for key, value in parse_qsl(decoded, keep_blank_values=True):
        claims[key] = value
    return claims


def verify_bonus_token(token, now=None):
    now = int(now or time.time())
    token = str(token).strip()
    if not token or len(token) > BONUS_TOKEN_MAX_LENGTH or '.' not in token:
        return BonusTokenResult(False, False, 'invalid-format', {})

    payload_segment, submitted_digest = token.split('.', 1)
    if len(submitted_digest) != 64:
        return BonusTokenResult(False, False, 'invalid-signature', {})

    try:
        payload = _decode_payload(payload_segment)
    except Exception:
        return BonusTokenResult(False, False, 'invalid-payload', {})

    expected_digest = _sign_payload(payload)
    if not hmac.compare_digest(submitted_digest, expected_digest):
        return BonusTokenResult(False, False, 'invalid-signature', {})

    claims = _parse_claims(payload)
    try:
        expires = int(claims.get('expires', '0'))
    except ValueError:
        return BonusTokenResult(False, False, 'invalid-expiry', claims)

    if expires < now:
        return BonusTokenResult(False, False, 'expired', claims)

    return BonusTokenResult(
        True,
        claims.get('role') == 'winner',
        'ok',
        claims,
    )
