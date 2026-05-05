from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=80)

    class Meta:
        db_table = 'posts'
        ordering = ['id']

    def __str__(self):
        return self.title


class Flag(models.Model):
    flag = models.CharField(max_length=120)
    source = models.CharField(max_length=80, default='flag')

    class Meta:
        db_table = 'flags'

    def __str__(self):
        return self.flag


class Submission(models.Model):
    user_id = models.PositiveIntegerField()
    owner_name = models.CharField(max_length=80)
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        db_table = 'submissions'
        ordering = ['id']

    def __str__(self):
        return f'{self.id}: {self.title}'


class HintState(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    unlocked_count = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hint_state'

    def __str__(self):
        return f'{self.key}: {self.unlocked_count}'
