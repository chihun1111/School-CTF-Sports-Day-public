from pathlib import Path

from django.test import TestCase

from .utils import EncryptedFlagStoreMixin, TEST_FLAGS


class FrontendChallengeTests(EncryptedFlagStoreMixin, TestCase):
    def test_html_comment_challenge_exposes_hidden_markup_flag(self):
        response = self.client.get('/campus/festival/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '컴퓨터공학과 미니 축제')
        self.assertContains(response, '체육대회 기간동안')
        self.assertContains(response, '재학생 모두 참가 가능')
        self.assertContains(response, f'archive={TEST_FLAGS["html_comment"]}')

    def test_sourcemap_challenge_exposes_map_file(self):
        page_response = self.client.get('/clubs/security/')
        app_js_response = self.client.get('/clubs/security/assets/main.js')
        map_response = self.client.get('/clubs/security/assets/main.js.map')

        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'CTF 미니 축제 안내')
        self.assertContains(page_response, '체육대회 기간')
        self.assertContains(page_response, '재학생 모두 참가 가능')
        self.assertContains(page_response, 'CTF 미니 축제')
        self.assertEqual(app_js_response.status_code, 200)
        self.assertEqual(map_response.status_code, 200)
        app_js = app_js_response.content.decode('utf-8')
        map_js = map_response.content.decode('utf-8')
        self.assertIn(
            'sourceMappingURL=/clubs/security/assets/main.js.map',
            app_js,
        )
        self.assertIn('CTF 미니 축제', app_js)
        self.assertIn('CTF 미니 축제', app_js)
        self.assertNotIn('Security Club', map_js)
        self.assertIn(TEST_FLAGS['sourcemap'], map_js)

    def test_localstorage_admin_challenge_uses_client_storage(self):
        page_response = self.client.get('/clubs/admin/')
        app_js_response = self.client.get('/clubs/admin/assets/app.js')

        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, '운영 현황')
        self.assertContains(page_response, 'CTF 미니 축제 운영')
        self.assertNotContains(page_response, '동아리 운영')
        self.assertNotContains(page_response, '관리자 패널')
        self.assertNotContains(page_response, 'Admin Only')
        self.assertEqual(app_js_response.status_code, 200)

        app_js = app_js_response.content.decode('utf-8')
        self.assertIn('localStorage.setItem("isAdmin", "false")', app_js)
        self.assertIn('isAdmin === "true"', app_js)
        self.assertNotIn('localStorage.setItem("role"', app_js)
        self.assertIn(TEST_FLAGS['localstorage_admin'], app_js)
