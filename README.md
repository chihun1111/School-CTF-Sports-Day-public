# 체육대회 CTF 미니 축제 공개 소스

체육대회 기간동안 진행하는 CTF 미니 축제용 Django 웹 서비스의 공개 소스입니다.

이 저장소는 참가자에게 공개해도 실제 플래그가 노출되지 않도록 구성되어 있습니다. 운영 플래그는 배포 서버에서 별도로 생성한 암호화 SQLite DB에서 런타임에만 읽습니다.

## 공개 범위

- 포함: Django 소스코드, 템플릿, 정적 파일, 테스트 코드, 환경변수 예시
- 제외: 실제 플래그, 운영자 풀이 문서, 운영 서버의 `.env`, 암호화 플래그 DB, 로컬 SQLite DB
- 4번 힌트에서 안내하는 소스코드 링크는 이 저장소를 사용합니다.

## 폴더 구조

```text
backend/
  config/         # Django 설정
  challenges/     # 문제 화면, API, 제출 검증 로직
    endpoints/    # 페이지와 API view
    management/   # 운영용 관리 명령
    migrations/   # DB 마이그레이션
    static/       # CSS, 이미지, 정적 리소스
    templates/    # HTML 템플릿
    tests/        # 테스트 코드
  private/        # 로컬 전용, git 제외
```

## 로컬 실행

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

실행 후 접속 주소:

```text
http://127.0.0.1:8000/
```

## 운영 환경변수

`.env`, `db.sqlite3`, `backend/private/`는 커밋하지 않습니다.

배포 서버에서는 `backend/.env`를 직접 만들고 아래 값을 설정합니다. 아래 값은 예시이며 실제 운영 값은 서버에서만 관리합니다.

```text
DJANGO_SECRET_KEY=change-this-for-school-deployment
CTF_FLAG_DB_PATH=private/ctf_flags.sqlite3
CTF_FLAG_DB_PASSWORD=change-this-strong-password
CTF_BONUS_TOKEN_KEY=change-this-bonus-token-key
CTF_HINT_ADMIN_CODE=change-this-hint-admin-code
```

암호화 플래그 DB는 서버 환경변수에서 실제 플래그를 읽어 생성합니다.

```bash
export CTF_FLAG_HTML_COMMENT="actual flag value"
export CTF_FLAG_SOURCEMAP="actual flag value"
export CTF_FLAG_LOCALSTORAGE_ADMIN="actual flag value"
export CTF_FLAG_DEBUG_API="actual flag value"
export CTF_FLAG_IDOR="actual flag value"
export CTF_FLAG_SQLI="actual flag value"
export CTF_FLAG_BONUS="actual special award value"
python manage.py create_flag_db
```

## 주요 경로

| 경로 | 설명 |
|---|---|
| `/` | 통합 포털 |
| `/flags/` | 일반 플래그 제출 페이지 |
| `/hints/` | 운영자가 단계별로 공개하는 힌트 페이지 |
| `/bonus/vault/` | 보너스 특별상 문제 페이지 |
| `/bonus/prize/` | 보호된 특별상 페이지 |
| `/campus/festival/` | 행사 일정 페이지 |
| `/clubs/security/` | 참가 안내 페이지 |
| `/clubs/admin/` | 운영 현황 페이지 |
| `/system/status/` | 학교 서비스 상태 페이지 |
| `/student/assignments/` | 제출 내역 페이지 |
| `/community/board/` | 학생 게시판 검색 페이지 |

## 검증

```bash
cd backend
python manage.py check
python manage.py test challenges
cd ..
rg -n "$(printf 'KDUCTF\\173')" .
git grep -n "$(printf 'KDUCTF\\173')" -- .
```

두 플래그 문자열 검색 명령은 공개 저장소에서 결과가 없어야 합니다.
