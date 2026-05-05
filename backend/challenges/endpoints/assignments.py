from django.shortcuts import get_object_or_404, render

from challenges.constants import CURRENT_USER
from challenges.flag_store import get_flag
from challenges.models import Submission


IDOR_FLAG_MARKER = '__RUNTIME_IDOR_FLAG__'


def index(request):
    submissions = Submission.objects.filter(user_id=CURRENT_USER['id'])
    return render(request, 'challenges/assignments/index.html', {
        'submissions': submissions,
        'current_user': CURRENT_USER,
    })


def detail(request, submission_id):
    # Intentionally vulnerable for the CTF: login is simulated, but ownership is not checked.
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.content == IDOR_FLAG_MARKER:
        submission.content = get_flag('idor')
    return render(request, 'challenges/assignments/detail.html', {
        'submission': submission,
        'current_user': CURRENT_USER,
    })
