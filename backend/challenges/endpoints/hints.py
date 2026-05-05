from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from challenges.hints import (
    HINTS,
    admin_code_matches,
    build_hint_cards,
    hint_unlock_rate_limited,
    lock_last_hint,
    unlock_next_hint,
)


HINT_ADMIN_SESSION_KEY = 'hint_admin_mode'


def _hint_context(request, message=None, error=None):
    cards = build_hint_cards()
    return {
        'hints': cards,
        'total_hints': len(HINTS),
        'unlocked_count': sum(1 for card in cards if card['unlocked']),
        'admin_mode': bool(request.session.get(HINT_ADMIN_SESSION_KEY)),
        'message': message,
        'error': error,
    }


@require_http_methods(['GET', 'POST'])
def index(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'login')

        if action == 'login':
            if hint_unlock_rate_limited(request):
                return render(request, 'portal/hints.html', _hint_context(
                    request,
                    error='시도가 너무 많습니다. 잠시 후 다시 시도하세요.',
                ), status=429)

            if not admin_code_matches(request.POST.get('admin_code', '')):
                return render(request, 'portal/hints.html', _hint_context(
                    request,
                    error='관리자 코드가 일치하지 않습니다.',
                ), status=403)

            request.session[HINT_ADMIN_SESSION_KEY] = True
            return render(request, 'portal/hints.html', _hint_context(
                request,
                message='관리자 모드가 활성화되었습니다.',
            ))

        if action == 'logout':
            request.session.pop(HINT_ADMIN_SESSION_KEY, None)
            return render(request, 'portal/hints.html', _hint_context(
                request,
                message='관리자 모드가 종료되었습니다.',
            ))

        if not request.session.get(HINT_ADMIN_SESSION_KEY):
            return render(request, 'portal/hints.html', _hint_context(
                request,
                error='관리자 모드가 필요합니다.',
            ), status=403)

        if action == 'unlock':
            unlocked_count, unlocked = unlock_next_hint()
            message = (
                f'힌트 {unlocked_count}번을 공개했습니다.'
                if unlocked
                else '모든 힌트가 공개되었습니다.'
            )
            return render(request, 'portal/hints.html', _hint_context(request, message=message))

        if action == 'lock':
            locked_hint_number, locked = lock_last_hint()
            message = (
                f'힌트 {locked_hint_number}번을 비공개로 되돌렸습니다.'
                if locked
                else '공개된 힌트가 없습니다.'
            )
            return render(request, 'portal/hints.html', _hint_context(request, message=message))

        return render(request, 'portal/hints.html', _hint_context(
            request,
            error='알 수 없는 관리자 동작입니다.',
        ), status=400)

    return render(request, 'portal/hints.html', _hint_context(request))
