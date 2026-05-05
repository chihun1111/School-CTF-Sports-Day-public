from django.db import migrations


SQLI_FLAG_PLACEHOLDER = 'runtime flag loads from encrypted DB'
IDOR_FLAG_MARKER = '__RUNTIME_IDOR_FLAG__'


def move_flags_to_runtime_store(apps, schema_editor):
    Flag = apps.get_model('challenges', 'Flag')
    Submission = apps.get_model('challenges', 'Submission')

    Flag.objects.update_or_create(
        id=1,
        defaults={
            'flag': SQLI_FLAG_PLACEHOLDER,
            'source': 'runtime-placeholder',
        },
    )
    Submission.objects.filter(title='비공개 과제 검토').update(content=IDOR_FLAG_MARKER)


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0005_update_ctf_mini_festival_copy'),
    ]

    operations = [
        migrations.RunPython(move_flags_to_runtime_store, migrations.RunPython.noop),
    ]
