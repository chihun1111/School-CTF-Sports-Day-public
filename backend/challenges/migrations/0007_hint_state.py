from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0006_remove_plaintext_runtime_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='HintState',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('unlocked_count', models.PositiveSmallIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'hint_state',
            },
        ),
    ]
