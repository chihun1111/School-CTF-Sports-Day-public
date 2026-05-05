import os
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, TestCase


class HintPageTests(TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_hint_page_starts_with_all_hints_locked(self):
        response = self.client.get('/hints/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '힌트 페이지')
        self.assertContains(response, 'Hint 1')
        self.assertContains(response, 'Hint 4')
        self.assertContains(response, '소스코드')
        self.assertContains(response, '관리자가 공개하면 표시됩니다.')
        self.assertNotContains(response, '브라우저 개발자 도구')

    def test_wrong_admin_code_does_not_unlock_or_echo_input(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            response = self.client.post('/hints/', {'admin_code': 'wrong-code'})

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '관리자 코드가 일치하지 않습니다.', status_code=403)
        self.assertNotContains(response, 'wrong-code', status_code=403)

        follow_up = self.client.get('/hints/')
        self.assertNotContains(follow_up, '브라우저 개발자 도구')

    def test_correct_admin_code_enables_admin_mode_without_unlocking_hint(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            response = self.client.post('/hints/', {'admin_code': 'school-admin-code'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '관리자 모드가 활성화되었습니다.')
        self.assertContains(response, '다음 힌트 공개')
        self.assertContains(response, '마지막 힌트 되돌리기')
        self.assertNotContains(response, '브라우저 개발자 도구')

    def test_admin_mode_unlocks_next_hint_for_everyone(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            self.client.post('/hints/', {'admin_code': 'school-admin-code'})
            response = self.client.post('/hints/', {'action': 'unlock'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '힌트 1번을 공개했습니다.')
        self.assertContains(response, '브라우저 개발자 도구')

        other_client = Client()
        follow_up = other_client.get('/hints/')
        self.assertContains(follow_up, '브라우저 개발자 도구')

    def test_admin_code_reveals_four_hints_and_stops(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            self.client.post('/hints/', {'admin_code': 'school-admin-code'})
            for _ in range(4):
                response = self.client.post('/hints/', {'action': 'unlock'})

            final_response = self.client.post('/hints/', {'action': 'unlock'})

        self.assertContains(response, '힌트 4번을 공개했습니다.')
        self.assertContains(final_response, '모든 힌트가 공개되었습니다.')

        page = self.client.get('/hints/')
        self.assertContains(page, '브라우저 개발자 도구')
        self.assertContains(page, '요청/응답')
        self.assertContains(page, '입력값이 서버에서 어떻게 처리되는지')
        self.assertContains(page, '공개 GitHub 저장소')
        self.assertContains(page, 'href="https://github.com/chihun1111/School-CTF-Sports-Day-public"')
        self.assertNotContains(page, 'Hint 5')

    def test_admin_mode_can_hide_last_public_hint(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            self.client.post('/hints/', {'admin_code': 'school-admin-code'})
            self.client.post('/hints/', {'action': 'unlock'})
            self.client.post('/hints/', {'action': 'unlock'})
            response = self.client.post('/hints/', {'action': 'lock'})

        self.assertContains(response, '힌트 2번을 비공개로 되돌렸습니다.')

        page = Client().get('/hints/')
        self.assertContains(page, '브라우저 개발자 도구')
        self.assertNotContains(page, '요청/응답')

        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            self.client.post('/hints/', {'action': 'lock'})
            final_response = self.client.post('/hints/', {'action': 'lock'})

        self.assertContains(final_response, '공개된 힌트가 없습니다.')
        empty_page = Client().get('/hints/')
        self.assertNotContains(empty_page, '브라우저 개발자 도구')

    def test_hint_admin_actions_require_admin_mode(self):
        response = self.client.post('/hints/', {'action': 'unlock'})

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '관리자 모드가 필요합니다.', status_code=403)

        page = self.client.get('/hints/')
        self.assertNotContains(page, '브라우저 개발자 도구')

    def test_admin_mode_can_be_ended(self):
        with patch.dict(os.environ, {'CTF_HINT_ADMIN_CODE': 'school-admin-code'}):
            self.client.post('/hints/', {'admin_code': 'school-admin-code'})
            response = self.client.post('/hints/', {'action': 'logout'})

        self.assertContains(response, '관리자 모드가 종료되었습니다.')
        self.assertNotContains(response, '다음 힌트 공개')
