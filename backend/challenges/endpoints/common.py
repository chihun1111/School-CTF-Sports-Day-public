import secrets
import time

from django.core.cache import cache
from django.core.signing import BadSignature
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from challenges.flags import (
    FLAG_CHECK_ATTEMPT_LIMIT,
    FLAG_CHECK_WINDOW_SECONDS,
    MAX_FLAG_SUBMISSIONS,
    build_flag_fields,
    check_submitted_flags,
)


FLAG_SUCCESS_COOKIE = 'flag_success'
FLAG_SUCCESS_TOKEN_SECONDS = 600


def _home_context(flag_result=None, flag_error=None):
    return {
        'flag_fields': build_flag_fields(),
        'flag_error': flag_error,
        'flag_result': flag_result,
    }


def home(request):
    return render(request, 'portal/index.html')


def flag_submit(request):
    return render(request, 'portal/flags/submit.html', _home_context())


def _flag_check_rate_key(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    client_ip = forwarded_for or request.META.get('REMOTE_ADDR', 'unknown')
    return f'flag-check-attempts:{client_ip}'


def _flag_check_rate_limited(request):
    now = time.time()
    cache_key = _flag_check_rate_key(request)
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


def _flag_success_key(token):
    return f'flag-check-success:{token}'


def _grant_flag_success(response):
    token = secrets.token_urlsafe(32)
    cache.set(_flag_success_key(token), True, FLAG_SUCCESS_TOKEN_SECONDS)
    response.set_signed_cookie(
        FLAG_SUCCESS_COOKIE,
        token,
        max_age=FLAG_SUCCESS_TOKEN_SECONDS,
        httponly=True,
        samesite='Lax',
    )
    return response


def flag_success(request):
    try:
        token = request.get_signed_cookie(
            FLAG_SUCCESS_COOKIE,
            max_age=FLAG_SUCCESS_TOKEN_SECONDS,
        )
    except (BadSignature, KeyError):
        return redirect('flag-submit')

    if not cache.get(_flag_success_key(token)):
        return redirect('flag-submit')

    return render(request, 'portal/flags/success.html')


@require_POST
def check_flags(request):
    if _flag_check_rate_limited(request):
        return render(request, 'portal/flags/submit.html', _home_context(
            flag_error='시도가 너무 많습니다. 잠시 후 다시 시도하세요.',
        ), status=429)

    submitted_flags = [
        request.POST.get(f'flag_{index}', '')
        for index in range(1, MAX_FLAG_SUBMISSIONS + 1)
    ]
    flag_result = check_submitted_flags(submitted_flags)

    if flag_result['correct_count'] == flag_result['total_count']:
        return _grant_flag_success(redirect('flag-success'))

    return render(request, 'portal/flags/submit.html', _home_context(
        flag_result=flag_result,
    ))
