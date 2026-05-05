import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from challenges.flag_store import get_flag


def html_comment(request):
    return render(request, 'portal/frontend/html_comment.html', {
        'html_comment_flag': get_flag('html_comment'),
    })


def sourcemap(request):
    return render(request, 'portal/frontend/sourcemap.html')


def sourcemap_js(request):
    script = """(()=>{const app=document.querySelector("#club-app");if(!app)return;app.innerHTML='<p class="eyebrow">Sports Day CTF</p><h2>CTF 미니 축제</h2><p class="lead-text">체육대회 기간동안 진행되며 재학생 모두 참가 가능입니다.</p><div class="feature-grid"><div><strong>운영 기간</strong><span>체육대회 기간동안</span></div><div><strong>미션 분야</strong><span>Web, Forensic, Crypto</span></div><div><strong>참가 대상</strong><span>재학생 모두 참가 가능</span></div></div>';})();
//# sourceMappingURL=/clubs/security/assets/main.js.map
"""
    return HttpResponse(script, content_type='application/javascript; charset=utf-8')


def sourcemap_map(request):
    flag = get_flag('sourcemap')
    return JsonResponse({
        'version': 3,
        'file': 'main.js',
        'sources': [
            '../../src/config/secret.js',
            '../../src/main.js',
        ],
        'sourcesContent': [
            (
                f'const BUILD_NOTE = {json.dumps(flag)};\n\n'
                'export function getBuildNote() {\n'
                '  return BUILD_NOTE;\n'
                '}\n'
            ),
            (
                "import { getBuildNote } from './config/secret.js';\n\n"
                "const app = document.querySelector('#club-app');\n\n"
                'if (app) {\n'
                '  app.innerHTML = `\\n'
                '    <p class="eyebrow">Sports Day CTF</p>\\n'
                '    <h2>CTF 미니 축제</h2>\\n'
                '    <p class="lead-text">체육대회 기간동안 진행되며 재학생 모두 참가 가능입니다.</p>\\n'
                '  `;\n'
                '}\n\n'
                'function debugOnly() {\n'
                '  return getBuildNote();\n'
                '}\n'
            ),
        ],
        'names': [],
        'mappings': '',
    })


def localstorage_admin(request):
    return render(request, 'portal/frontend/localstorage_admin.html')


def localstorage_admin_js(request):
    flag = json.dumps(get_flag('localstorage_admin'))
    script = f"""function ensureDefaultRole() {{
  if (!localStorage.getItem("role")) {{
    localStorage.setItem("role", "guest");
  }}
}}

function renderByRole() {{
  const role = localStorage.getItem("role") || "guest";
  const userState = document.querySelector("#user-state");
  const adminPanel = document.querySelector("#admin-panel");
  const flag = document.querySelector("#flag");

  userState.innerText = role;

  if (role === "admin") {{
    adminPanel.hidden = false;
    flag.innerText = {flag};
  }} else {{
    adminPanel.hidden = true;
    flag.innerText = "";
  }}
}}

ensureDefaultRole();
renderByRole();
"""
    return HttpResponse(script, content_type='application/javascript; charset=utf-8')
