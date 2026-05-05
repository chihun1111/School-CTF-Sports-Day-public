from django.db import migrations


SQLI_FLAG_PLACEHOLDER = 'runtime flag loads from encrypted DB'


def update_sqli_flag(apps, schema_editor):
    Flag = apps.get_model('challenges', 'Flag')
    Flag.objects.update_or_create(
        id=1,
        defaults={
            'flag': SQLI_FLAG_PLACEHOLDER,
            'source': 'runtime-placeholder',
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0003_flag_source'),
    ]

    operations = [
        migrations.RunPython(update_sqli_flag, migrations.RunPython.noop),
    ]
