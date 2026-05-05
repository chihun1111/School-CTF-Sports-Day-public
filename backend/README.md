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
      assignments.py
      community.py
      common.py
      event_stations.py
      status_panel.py
    static/
      challenges/
        status_panel/
      portal/
        styles.css
    templates/
      challenges/
        assignments/
        community/
        status_panel/
      portal/
        base.html
        index.html
        stations/
    migrations/
  private/        # local only, ignored by git
```

## Primary Routes

- `/` - unified challenge portal
- `/flags/` - dedicated flag submission page for up to six flags
- `/flags/check/` - flag submission checker
- `/flags/success/` - special completion page after all flags are correct
- `/campus/festival/` - event station
- `/clubs/security/` - event station
- `/clubs/admin/` - event station
- `/system/status/` - service status page
- `/student/assignments/` - assignment list
- `/student/assignments/<id>/` - assignment detail
- `/community/board/` - community board search
- `/status/` - service status page
- `/api/status` - visible status API
- `/api/debug` - internal diagnostics API
- `/robots.txt` - diagnostics hint
- `/submissions/` - assignment list
- `/submissions/<id>/` - assignment detail
- `/search/` - intentionally vulnerable SQL search

Operator and solution documents are kept outside this public project tree.

## Verification

```powershell
python manage.py check
python manage.py test challenges
```
