from django.urls import path

from .endpoints import common, debug_api, frontend, idor, sqli


urlpatterns = [
    path('', common.home, name='home'),
    path('flags/', common.flag_submit, name='flag-submit'),
    path('flags/check/', common.check_flags, name='flag-check'),
    path('flags/success/', common.flag_success, name='flag-success'),
    path('campus/festival/', frontend.html_comment, name='campus-festival'),
    path('clubs/security/', frontend.sourcemap, name='clubs-security'),
    path('clubs/security/assets/main.js', frontend.sourcemap_js, name='clubs-security-js'),
    path('clubs/security/assets/main.js.map', frontend.sourcemap_map, name='clubs-security-map'),
    path('clubs/admin/', frontend.localstorage_admin, name='clubs-admin'),
    path('clubs/admin/assets/app.js', frontend.localstorage_admin_js, name='clubs-admin-js'),
    path('system/status/', debug_api.status_page, name='system-status'),
    path('student/assignments/', idor.index, name='student-assignments'),
    path('student/assignments/<int:submission_id>/', idor.detail, name='student-assignment-detail'),
    path('community/board/', sqli.search, name='community-board'),
    path('frontend/html-comment/', frontend.html_comment, name='frontend-html-comment'),
    path('frontend/sourcemap/', frontend.sourcemap, name='frontend-sourcemap'),
    path('frontend/localstorage-admin/', frontend.localstorage_admin, name='frontend-localstorage-admin'),
    path('frontend-01-html-comment/', frontend.html_comment, name='frontend-01-html-comment'),
    path('frontend-02-sourcemap/', frontend.sourcemap, name='frontend-02-sourcemap'),
    path('frontend-03-localstorage-admin/', frontend.localstorage_admin, name='frontend-03-localstorage-admin'),
    path('status/', debug_api.status_page, name='status-page'),
    path('debug-api/', debug_api.status_page, name='debug-api'),
    path('backend-01-debug-api/', debug_api.status_page, name='backend-01-debug-api'),
    path('backend-02-idor/', idor.index, name='backend-02-idor'),
    path('backend-03-sqli/', sqli.search, name='backend-03-sqli'),
    path('api/status', debug_api.api_status, name='api-status'),
    path('api/debug', debug_api.api_debug, name='api-debug'),
    path('robots.txt', debug_api.robots_txt, name='robots-txt'),
    path('submissions/', idor.index, name='submissions-index'),
    path('submissions/<int:submission_id>/', idor.detail, name='submission-detail'),
    path('search/', sqli.search, name='search'),
]
