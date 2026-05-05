# School CTF Sports Day

Public source for a Django-based school CTF mini festival service.

The project is built so the source repository can be public without exposing
production flags. Runtime flag values are loaded from an encrypted SQLite DB
that is generated separately on the deployment server.

## Layout

```text
backend/
  config/
  challenges/
    endpoints/
    management/
    migrations/
    static/
    templates/
    tests/
  private/        # local only, ignored by git
```

## Local Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

The development server runs at `http://127.0.0.1:8000/`.

## Runtime Flags

Do not commit `.env`, `db.sqlite3`, or `backend/private/`.

Create `backend/.env` on the deployment server:

```text
DJANGO_SECRET_KEY=change-this-for-school-deployment
CTF_FLAG_DB_PATH=private/ctf_flags.sqlite3
CTF_FLAG_DB_PASSWORD=change-this-strong-password
```

Then generate the encrypted flag DB from server-side environment variables:

```bash
export CTF_FLAG_HTML_COMMENT="actual flag value"
export CTF_FLAG_SOURCEMAP="actual flag value"
export CTF_FLAG_LOCALSTORAGE_ADMIN="actual flag value"
export CTF_FLAG_DEBUG_API="actual flag value"
export CTF_FLAG_IDOR="actual flag value"
export CTF_FLAG_SQLI="actual flag value"
python manage.py create_flag_db
```

## Verification

```bash
cd backend
python manage.py check
python manage.py test challenges
cd ..
rg -n "$(printf 'KDUCTF\\173')" .
git grep -n "$(printf 'KDUCTF\\173')" -- .
```

The two flag scans should return no matches in this public repository.
