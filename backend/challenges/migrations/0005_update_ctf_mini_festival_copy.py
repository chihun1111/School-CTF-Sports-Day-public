from django.db import migrations


def update_copy(apps, schema_editor):
    Post = apps.get_model('challenges', 'Post')

    Post.objects.filter(author='ctf_staff').update(
        title='CTF 미니 축제 참가 안내',
        content='체육대회 기간동안 진행되는 CTF 미니 축제는 재학생 모두 참가 가능입니다.',
        author='ctf_staff',
    )


def restore_copy(apps, schema_editor):
    Post = apps.get_model('challenges', 'Post')

    Post.objects.filter(author='ctf_staff').update(
        title='CTF 미니 축제 참가 안내',
        content='체육대회 기간동안 진행되는 CTF 미니 축제는 재학생 모두 참가 가능입니다.',
        author='ctf_staff',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0004_update_sqli_flag'),
    ]

    operations = [
        migrations.RunPython(update_copy, restore_copy),
    ]
