from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from challenges.flag_store import get_flag


def status_page(request):
    return render(request, 'challenges/status_panel/status.html')


def api_status(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'school-backend',
        'message': 'server is running',
    })


def api_debug(request):
    return JsonResponse({
        'status': 'ok',
        'mode': 'development',
        'debug': True,
        'server': 'kductf-backend-03',
        'flag': get_flag('debug_api'),
    })


def robots_txt(request):
    return HttpResponse(
        'User-agent: *\nDisallow: /api/debug\n',
        content_type='text/plain',
    )
