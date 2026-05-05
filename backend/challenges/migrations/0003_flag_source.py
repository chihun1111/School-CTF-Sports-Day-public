from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0002_seed_challenge_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='flag',
            name='source',
            field=models.CharField(default='flag', max_length=80),
        ),
    ]
