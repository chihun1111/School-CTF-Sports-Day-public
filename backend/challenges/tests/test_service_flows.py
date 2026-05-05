from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import TestCase

from .utils import EncryptedFlagStoreMixin, TEST_FLAGS


class BackendChallengeTests(EncryptedFlagStoreMixin, TestCase):
    def test_status_page_and_hints_are_reachable(self):
        page_response = self.client.get('/system/status/')
        robots_response = self.client.get('/robots.txt')
        app_js_path = finders.find('challenges/status_panel/app.js')

        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, '학교 서비스 상태 페이지')
        self.assertContains(robots_response, 'Disallow: /api/debug')
        self.assertIsNotNone(app_js_path)
        self.assertIn('/api/debug', Path(app_js_path).read_text(encoding='utf-8'))

    def test_debug_api_exposes_flag(self):
        response = self.client.get('/api/debug')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['flag'], TEST_FLAGS['debug_api'])

    def test_submissions_index_shows_only_current_user_items(self):
        response = self.client.get('/student/assignments/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '웹프로그래밍 과제')
        self.assertContains(response, '데이터베이스 과제')
        self.assertNotContains(response, TEST_FLAGS['idor'])

    def test_idor_detail_exposes_other_submission(self):
        response = self.client.get('/student/assignments/4/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TEST_FLAGS['idor'])

    def test_sqli_search_shows_normal_posts_and_errors(self):
        normal_response = self.client.get('/community/board/', {'q': '과제'})
        error_response = self.client.get('/community/board/', {'q': "'"})

        self.assertEqual(normal_response.status_code, 200)
        self.assertContains(normal_response, '프로그래밍 과제 안내')
        self.assertContains(error_response, 'SQL Error')

    def test_board_uses_ctf_mini_festival_copy(self):
        response = self.client.get('/community/board/', {'q': 'CTF'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CTF 미니 축제 참가 안내')
        self.assertContains(response, 'CTF 미니 축제 참가 안내')

    def test_sqli_search_can_union_flags_table(self):
        payload = "' UNION SELECT * FROM flags--"
        response = self.client.get('/community/board/', {'q': payload})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TEST_FLAGS['sqli'])
