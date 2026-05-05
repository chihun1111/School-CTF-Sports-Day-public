from django.db import connection
from django.shortcuts import render

from challenges.flag_store import get_flag
from challenges.models import Flag


SQLI_FLAG_SOURCE = 'runtime-sqli'


def _ensure_runtime_sqli_flag():
    Flag.objects.update_or_create(
        source=SQLI_FLAG_SOURCE,
        defaults={'flag': get_flag('sqli')},
    )


def search(request):
    _ensure_runtime_sqli_flag()
    q = request.GET.get('q', '')
    rows = []
    error = None
    sql = (
        "SELECT id, title, author "
        "FROM posts "
        f"WHERE title LIKE '%{q}%'"
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = [
                {'id': row[0], 'title': row[1], 'author': row[2]}
                for row in cursor.fetchall()
            ]
    except Exception as exc:
        error = f'SQL Error: {exc}'

    return render(request, 'challenges/community/search.html', {
        'query': q,
        'rows': rows,
        'error': error,
    })
