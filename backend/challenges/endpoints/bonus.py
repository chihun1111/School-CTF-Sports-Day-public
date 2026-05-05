import secrets
import time
from urllib.parse import urlencode

from django.core.cache import cache
from django.core.signing import BadSignature
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from challenges.bonus_tokens import issue_guest_token, verify_bonus_token
from challenges.flag_store import get_flag
from challenges.flags import (
    FLAG_CHECK_ATTEMPT_LIMIT,
    FLAG_CHECK_WINDOW_SECONDS,
    build_flag_fields,
    check_bonus_flag,
)


BONUS_SUCCESS_COOKIE = 'bonus_success'
BONUS_VAULT_COOKIE = 'vault_ticket'
BONUS_SUCCESS_TOKEN_SECONDS = 600
BONUS_VAULT_TOKEN_SECONDS = 3600


def _bonus_success_key(token):
    return f'bonus-success:{token}'


def _bonus_prize_url(token):
    return f'{reverse("bonus-prize")}?{urlencode({"access": token})}'


def _reject_bonus_success(token=None):
    if token:
        cache.delete(_bonus_success_key(token))
    response = redirect('bonus-vault')
    response.delete_cookie(BONUS_SUCCESS_COOKIE, samesite='Lax')
    return response


def _read_bonus_success_cookie(request):
    try:
        return request.get_signed_cookie(
            BONUS_SUCCESS_COOKIE,
            max_age=BONUS_SUCCESS_TOKEN_SECONDS,
        )
    except (BadSignature, KeyError):
        return None


def _grant_bonus_success():
    token = secrets.token_urlsafe(32)
    cache.set(_bonus_success_key(token), True, BONUS_SUCCESS_TOKEN_SECONDS)
    response = redirect(_bonus_prize_url(token))
    response.set_signed_cookie(
        BONUS_SUCCESS_COOKIE,
        token,
        max_age=BONUS_SUCCESS_TOKEN_SECONDS,
        httponly=True,
        samesite='Lax',
    )
    return response


def _vault_context(error=None):
    return {
        'error': error,
    }


def _flag_submit_context(bonus_error=None):
    return {
        'flag_fields': build_flag_fields(),
        'flag_error': None,
        'flag_result': None,
        'bonus_error': bonus_error,
    }


def _bonus_flag_rate_key(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    client_ip = forwarded_for or request.META.get('REMOTE_ADDR', 'unknown')
    return f'bonus-flag-attempts:{client_ip}'


def _bonus_flag_rate_limited(request):
    now = time.time()
    cache_key = _bonus_flag_rate_key(request)
    attempts = [
        timestamp
        for timestamp in cache.get(cache_key, [])
        if now - float(timestamp) < FLAG_CHECK_WINDOW_SECONDS
    ]

    if len(attempts) >= FLAG_CHECK_ATTEMPT_LIMIT:
        cache.set(cache_key, attempts, FLAG_CHECK_WINDOW_SECONDS)
        return True

    attempts.append(now)
    cache.set(cache_key, attempts, FLAG_CHECK_WINDOW_SECONDS)
    return False


def vault(request):
    response = render(request, 'portal/bonus/vault.html', _vault_context())
    response.set_cookie(
        BONUS_VAULT_COOKIE,
        issue_guest_token(),
        max_age=BONUS_VAULT_TOKEN_SECONDS,
        httponly=False,
        samesite='Lax',
    )
    return response


@require_POST
def check(request):
    result = verify_bonus_token(request.POST.get('ticket', request.POST.get('token', '')))
    if result.valid and result.winner:
        return _grant_bonus_success()

    status = 403 if result.valid else 400
    if result.valid:
        message = '확인 대상이 아닙니다.'
    elif result.reason in {'invalid-format', 'invalid-payload'}:
        message = '확인 코드 형식이 맞지 않습니다.'
    else:
        message = '확인에 실패했습니다.'
    return render(request, 'portal/bonus/vault.html', _vault_context(message), status=status)


@require_POST
def flag_check(request):
    if _bonus_flag_rate_limited(request):
        return render(request, 'portal/flags/submit.html', _flag_submit_context(
            bonus_error='시도가 너무 많습니다. 잠시 후 다시 시도하세요.',
        ), status=429)

    if check_bonus_flag(request.POST.get('bonus_flag', '')):
        return _grant_bonus_success()

    return render(request, 'portal/flags/submit.html', _flag_submit_context(
        bonus_error='보너스 플래그가 일치하지 않습니다.',
    ), status=403)


def prize(request):
    token = _read_bonus_success_cookie(request)
    access_token = request.GET.get('access', '')

    if not token or not access_token:
        return _reject_bonus_success(token)

    if not secrets.compare_digest(token, access_token):
        return _reject_bonus_success(token)

    if not cache.get(_bonus_success_key(token)):
        return _reject_bonus_success(token)

    cache.delete(_bonus_success_key(token))
    response = render(request, 'portal/bonus/prize.html', {
        'bonus_flag': get_flag('bonus'),
    })
    response.delete_cookie(BONUS_SUCCESS_COOKIE, samesite='Lax')
    return response
