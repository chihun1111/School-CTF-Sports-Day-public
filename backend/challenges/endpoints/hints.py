from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from challenges.hints import (
    HINTS,
    admin_code_matches,
    build_hint_cards,
    hint_unlock_rate_limited,
    unlock_next_hint,
)


def _hint_context(message=None, error=None):
    cards = build_hint_cards()
    return {
        'hints': cards,
        'total_hints': len(HINTS),
        'unlocked_count': sum(1 for card in cards if card['unlocked']),
        'message': message,
        'error': error,
    }


@require_http_methods(['GET', 'POST'])
def index(request):
    if request.method == 'POST':
        if hint_unlock_rate_limited(request):
            return render(request, 'portal/hints.html', _hint_context(
                error='시도가 너무 많습니다. 잠시 후 다시 시도하세요.',
            ), status=429)

        if not admin_code_matches(request.POST.get('admin_code', '')):
            return render(request, 'portal/hints.html', _hint_context(
                error='관리자 코드가 일치하지 않습니다.',
            ), status=403)

        unlocked_count, unlocked = unlock_next_hint()
        message = (
            f'힌트 {unlocked_count}번을 공개했습니다.'
            if unlocked
            else '모든 힌트가 공개되었습니다.'
        )
        return render(request, 'portal/hints.html', _hint_context(message=message))

    return render(request, 'portal/hints.html', _hint_context())
