from django.contrib import admin

from .models import Flag, Post, Submission


admin.site.register(Post)
admin.site.register(Flag)
admin.site.register(Submission)
