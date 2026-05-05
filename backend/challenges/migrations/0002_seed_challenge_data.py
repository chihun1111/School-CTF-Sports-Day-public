from django.db import migrations


SQLI_FLAG_PLACEHOLDER = 'runtime flag loads from encrypted DB'
IDOR_FLAG_MARKER = '__RUNTIME_IDOR_FLAG__'


def seed_data(apps, schema_editor):
    Post = apps.get_model('challenges', 'Post')
    Flag = apps.get_model('challenges', 'Flag')
    Submission = apps.get_model('challenges', 'Submission')

    Post.objects.bulk_create([
        Post(
            title='중간고사 일정 안내',
            content='중간고사는 다음 주부터 시작합니다.',
            author='admin',
        ),
        Post(
            title='CTF 미니 축제 참가 안내',
            content='체육대회 기간동안 진행되는 CTF 미니 축제는 재학생 모두 참가 가능입니다.',
            author='ctf_staff',
        ),
        Post(
            title='프로그래밍 과제 안내',
            content='이번 주 과제는 게시판 만들기입니다.',
            author='professor',
        ),
        Post(
            title='학교 축제 일정',
            content='컴퓨터공학과 부스 운영 예정입니다.',
            author='student_council',
        ),
    ])

    Flag.objects.create(flag=SQLI_FLAG_PLACEHOLDER)

    Submission.objects.bulk_create([
        Submission(
            user_id=1,
            owner_name='student01',
            title='웹프로그래밍 과제',
            content='게시판 CRUD를 구현했습니다.',
        ),
        Submission(
            user_id=1,
            owner_name='student01',
            title='데이터베이스 과제',
            content='ERD와 SQL 쿼리를 작성했습니다.',
        ),
        Submission(
            user_id=2,
            owner_name='student02',
            title='네트워크 과제',
            content='HTTP와 DNS를 정리했습니다.',
        ),
        Submission(
            user_id=3,
            owner_name='admin',
            title='비공개 과제 검토',
            content=IDOR_FLAG_MARKER,
        ),
    ])


def unseed_data(apps, schema_editor):
    Post = apps.get_model('challenges', 'Post')
    Flag = apps.get_model('challenges', 'Flag')
    Submission = apps.get_model('challenges', 'Submission')

    Post.objects.all().delete()
    Flag.objects.all().delete()
    Submission.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
