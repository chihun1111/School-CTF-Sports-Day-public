import hmac

from challenges.flag_store import get_all_flags


NORMAL_FLAG_NAMES = (
    'html_comment',
    'sourcemap',
    'localstorage_admin',
    'debug_api',
    'idor',
    'sqli',
)
MAX_FLAG_SUBMISSIONS = 6
MAX_FLAG_LENGTH = 96
FLAG_CHECK_ATTEMPT_LIMIT = 10
FLAG_CHECK_WINDOW_SECONDS = 60


def normalize_flag(value):
    value = str(value).strip()
    if len(value) > MAX_FLAG_LENGTH:
        return ''
    return value


def build_flag_fields():
    return [
        {
            'name': f'flag_{index}',
            'label': f'플래그 {index}',
            'value': '',
        }
        for index in range(1, MAX_FLAG_SUBMISSIONS + 1)
    ]


def _matches_any_flag(submitted_flag, expected_flags):
    return any(
        hmac.compare_digest(submitted_flag, expected_flag)
        for expected_flag in expected_flags
    )


def check_submitted_flags(values):
    expected_flags = {
        normalize_flag(flag)
        for name, flag in get_all_flags().items()
        if name in NORMAL_FLAG_NAMES
        if normalize_flag(flag)
    }
    submitted_flags = [
        normalize_flag(value)
        for value in list(values)[:MAX_FLAG_SUBMISSIONS]
    ]
    correct_flags = {
        flag
        for flag in submitted_flags
        if flag
        if _matches_any_flag(flag, expected_flags)
    }

    return {
        'correct_count': len(correct_flags),
        'total_count': len(expected_flags),
        'submitted_count': sum(1 for flag in submitted_flags if flag),
        'max_count': MAX_FLAG_SUBMISSIONS,
    }


def check_bonus_flag(value):
    submitted_flag = normalize_flag(value)
    expected_flag = normalize_flag(get_all_flags()['bonus'])
    return bool(
        submitted_flag
        and expected_flag
        and hmac.compare_digest(submitted_flag, expected_flag)
    )
