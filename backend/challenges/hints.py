import hmac
import os
import time

from django.core.cache import cache
from django.db import transaction

from challenges.models import HintState


PUBLIC_SOURCE_URL = 'https://github.com/chihun1111/School-CTF-Sports-Day-public'

HINTS = (
    {
        'number': 1,
        'title': '화면 밖의 단서',
        'body': '페이지에 보이지 않는 값도 브라우저 개발자 도구에서 확인할 수 있습니다.',
    },
    {
        'number': 2,
        'title': '브라우저 기록',
        'body': '요청/응답, 쿠키, Local Storage처럼 브라우저가 저장하는 값을 함께 확인하세요.',
    },
    {
        'number': 3,
        'title': '서버의 반응',
        'body': '입력값이 서버에서 어떻게 처리되는지 URL, 파라미터, 응답 형태를 비교하세요.',
    },
    {
        'number': 4,
        'title': '소스코드',
        'body': '공개 GitHub 저장소에서 소스코드를 확인하세요.',
        'url': PUBLIC_SOURCE_URL,
        'link_label': '공개 GitHub 저장소',
    },
)

HINT_STATE_KEY = 'global'
HINT_UNLOCK_ATTEMPT_LIMIT = 10
HINT_UNLOCK_WINDOW_SECONDS = 60


def get_hint_state():
    state, _ = HintState.objects.get_or_create(
        key=HINT_STATE_KEY,
        defaults={'unlocked_count': 0},
    )
    return state


def build_hint_cards():
    unlocked_count = min(get_hint_state().unlocked_count, len(HINTS))
    return [
        {
            **hint,
            'unlocked': hint['number'] <= unlocked_count,
        }
        for hint in HINTS
    ]


def admin_code_matches(submitted_code):
    expected_code = os.environ.get('CTF_HINT_ADMIN_CODE', '')
    submitted_code = str(submitted_code or '').strip()
    return bool(
        expected_code
        and submitted_code
        and hmac.compare_digest(submitted_code, expected_code)
    )


def unlock_next_hint():
    with transaction.atomic():
        state, _ = HintState.objects.select_for_update().get_or_create(
            key=HINT_STATE_KEY,
            defaults={'unlocked_count': 0},
        )

        if state.unlocked_count >= len(HINTS):
            return state.unlocked_count, False

        state.unlocked_count += 1
        state.save(update_fields=['unlocked_count', 'updated_at'])
        return state.unlocked_count, True


def lock_last_hint():
    with transaction.atomic():
        state, _ = HintState.objects.select_for_update().get_or_create(
            key=HINT_STATE_KEY,
            defaults={'unlocked_count': 0},
        )

        if state.unlocked_count <= 0:
            return 0, False

        locked_hint_number = state.unlocked_count
        state.unlocked_count -= 1
        state.save(update_fields=['unlocked_count', 'updated_at'])
        return locked_hint_number, True


def hint_unlock_rate_key(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    client_ip = forwarded_for or request.META.get('REMOTE_ADDR', 'unknown')
    return f'hint-unlock-attempts:{client_ip}'


def hint_unlock_rate_limited(request):
    now = time.time()
    cache_key = hint_unlock_rate_key(request)
    attempts = [
        timestamp
        for timestamp in cache.get(cache_key, [])
        if now - float(timestamp) < HINT_UNLOCK_WINDOW_SECONDS
    ]

    if len(attempts) >= HINT_UNLOCK_ATTEMPT_LIMIT:
        cache.set(cache_key, attempts, HINT_UNLOCK_WINDOW_SECONDS)
        return True

    attempts.append(now)
    cache.set(cache_key, attempts, HINT_UNLOCK_WINDOW_SECONDS)
    return False
