# Django 백엔드 실행 안내

이 디렉터리는 CTF 미니 축제 웹 서비스를 제공하는 Django 프로젝트입니다.

## 실행 방법

Windows PowerShell 기준:

```powershell
cd D:\work\CTF\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

macOS/Linux 기준:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

개발 서버 주소:

```text
http://127.0.0.1:8000/
```

## 런타임 비밀값

`.env`와 암호화 플래그 DB는 커밋하지 않습니다. 학교 배포 서버에서는 `backend/.env`를 직접 만들고 아래 값을 설정합니다.

```text
DJANGO_SECRET_KEY=change-this-for-school-deployment
CTF_FLAG_DB_PATH=private/ctf_flags.sqlite3
CTF_FLAG_DB_PASSWORD=change-this-strong-password
CTF_BONUS_TOKEN_KEY=change-this-bonus-token-key
CTF_HINT_ADMIN_CODE=change-this-hint-admin-code
```

각 값의 역할:

| 환경변수 | 역할 |
|---|---|
| `DJANGO_SECRET_KEY` | Django 서명과 보안 기능에 사용하는 서버 전용 키 |
| `CTF_FLAG_DB_PATH` | 암호화 플래그 DB 경로 |
| `CTF_FLAG_DB_PASSWORD` | 암호화 플래그 DB 복호화 비밀번호 |
| `CTF_BONUS_TOKEN_KEY` | 보너스 특별상 확인 코드 서명 키 |
| `CTF_HINT_ADMIN_CODE` | `/hints/`에서 힌트를 공개할 때 사용하는 관리자 코드 |

## 암호화 플래그 DB 생성

운영 서버에서 실제 플래그를 환경변수로 넣은 뒤 DB를 생성합니다.

```powershell
$env:CTF_FLAG_HTML_COMMENT="actual flag value"
$env:CTF_FLAG_SOURCEMAP="actual flag value"
$env:CTF_FLAG_LOCALSTORAGE_ADMIN="actual flag value"
$env:CTF_FLAG_DEBUG_API="actual flag value"
$env:CTF_FLAG_IDOR="actual flag value"
$env:CTF_FLAG_SQLI="actual flag value"
$env:CTF_FLAG_BONUS="actual special award value"
python manage.py create_flag_db
```

소스코드에는 실제 플래그를 넣지 않습니다. 배포된 페이지와 문제 API는 요청 시점에 암호화 DB에서 플래그를 읽습니다.

## 주요 경로

| 경로 | 설명 |
|---|---|
| `/` | 통합 포털 |
| `/flags/` | 일반 플래그 최대 6개 제출 |
| `/flags/check/` | 일반 플래그 채점 |
| `/flags/success/` | 일반 플래그 6개 정답 후 이동하는 특별 페이지 |
| `/hints/` | 운영자가 단계별로 공개하는 힌트 페이지 |
| `/bonus/vault/` | 보너스 특별상 확인 코드 문제 |
| `/bonus/check/` | 보너스 확인 코드 검증 |
| `/bonus/flag-check/` | 보너스 플래그 제출 |
| `/bonus/prize/` | 보호된 특별상 페이지 |
| `/campus/festival/` | 행사 일정 페이지 |
| `/clubs/security/` | 참가 안내 페이지 |
| `/clubs/admin/` | 운영 현황 페이지 |
| `/system/status/` | 서비스 상태 페이지 |
| `/student/assignments/` | 제출 내역 목록 |
| `/student/assignments/<id>/` | 제출 내역 상세 |
| `/community/board/` | 학생 게시판 검색 |
| `/api/status` | 공개 상태 API |
| `/api/debug` | 문제용 디버그 API |
| `/robots.txt` | 디버그 API 단서 |

운영자 문서와 풀이 문서는 이 공개 저장소 밖에서 관리합니다.

## 검증

```powershell
python manage.py check
python manage.py test challenges
```
