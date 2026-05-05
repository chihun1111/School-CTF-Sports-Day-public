# Django Backend

## Setup

```powershell
cd D:\work\CTF\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

The development server runs at http://127.0.0.1:8000/.

## Runtime Secrets

Do not commit `.env` or the encrypted flag DB. For school deployment, create
`backend/.env` on the server and set these values:

```text
DJANGO_SECRET_KEY=change-this-for-school-deployment
CTF_FLAG_DB_PATH=private/ctf_flags.sqlite3
CTF_FLAG_DB_PASSWORD=change-this-strong-password
```

Create the encrypted DB from server-side environment variables:

```powershell
$env:CTF_FLAG_HTML_COMMENT="actual flag value"
$env:CTF_FLAG_SOURCEMAP="actual flag value"
$env:CTF_FLAG_LOCALSTORAGE_ADMIN="actual flag value"
$env:CTF_FLAG_DEBUG_API="actual flag value"
$env:CTF_FLAG_IDOR="actual flag value"
$env:CTF_FLAG_SQLI="actual flag value"
python manage.py create_flag_db
```

The source code contains only runtime lookup code. The deployed pages and
challenge endpoints read flag values from the encrypted DB at request time.

## Project Layout

```text
backend/
  config/
  challenges/
    endpoints/
      common.py
      debug_api.py
      frontend.py
      idor.py
      sqli.py
    static/
      challenges/
        debug_api/
      portal/
        styles.css
    templates/
      challenges/
        debug_api/
        idor/
        sqli/
      portal/
        base.html
        index.html
        frontend/
    migrations/
  private/        # local only, ignored by git
```

## Challenge Routes

- `/` - unified frontend/backend challenge portal
- `/flags/` - dedicated flag submission page for up to six flags
- `/flags/check/` - flag submission checker
- `/flags/success/` - special completion page after all flags are correct
- `/campus/festival/` - sports-day CTF mini festival frontend challenge
- `/clubs/security/` - CTF mini festival Source Map frontend challenge
- `/clubs/admin/` - CTF mini festival operations localStorage frontend challenge
- `/system/status/` - exposed debug API challenge entry page
- `/student/assignments/` - IDOR challenge list
- `/student/assignments/<id>/` - intentionally missing ownership check
- `/community/board/` - intentionally vulnerable SQL search
- `/frontend/html-comment/` - HTML comment frontend challenge
- `/frontend/sourcemap/` - Source Map frontend challenge
- `/frontend/localstorage-admin/` - localStorage admin frontend challenge
- `/frontend-01-html-comment/` - document service alias
- `/frontend-02-sourcemap/` - document service alias
- `/frontend-03-localstorage-admin/` - document service alias
- `/status/` - exposed debug API challenge entry page
- `/debug-api/` - compatibility alias for the debug API challenge
- `/api/status` - visible status API
- `/api/debug` - leaked debug API
- `/robots.txt` - debug endpoint hint
- `/submissions/` - IDOR challenge list
- `/submissions/<id>/` - intentionally missing ownership check
- `/search/` - intentionally vulnerable SQL search
- `/backend-01-debug-api/` - document service alias
- `/backend-02-idor/` - document service alias
- `/backend-03-sqli/` - document service alias

Operator and solution documents are kept outside this public project tree.

## Verification

```powershell
python manage.py check
python manage.py test challenges
```
