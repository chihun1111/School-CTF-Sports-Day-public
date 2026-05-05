from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.template.loader import get_template
from django.test import TestCase

from .utils import EncryptedFlagStoreMixin, TEST_FLAGS


ALL_FLAGS = {
    'flag_1': TEST_FLAGS['html_comment'],
    'flag_2': TEST_FLAGS['sourcemap'],
    'flag_3': TEST_FLAGS['localstorage_admin'],
    'flag_4': TEST_FLAGS['debug_api'],
    'flag_5': TEST_FLAGS['idor'],
    'flag_6': TEST_FLAGS['sqli'],
}


class PortalTests(EncryptedFlagStoreMixin, TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_home_uses_django_app_templates_and_static_assets(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '컴퓨터공학과 통합 서비스')
        self.assertContains(response, '행사 안내')
        self.assertContains(response, 'CTF 미니 축제')
        self.assertContains(response, '운영 현황')
        self.assertContains(response, '체육대회 기간')
        self.assertContains(response, '재학생 모두 참가 가능')
        self.assertContains(response, '학교 서비스 상태 페이지')
        self.assertContains(response, '제출 내역')
        self.assertContains(response, '학생 게시판')
        self.assertContains(response, '보너스 특별상 접수')
        self.assertIsNotNone(get_template('portal/index.html'))
        self.assertIsNotNone(finders.find('portal/styles.css'))
        self.assertFalse(Path(__file__).resolve().parents[3].joinpath('frontend').exists())

    def test_home_does_not_leak_flags_before_submission(self):
        response = self.client.get('/')

        for flag in TEST_FLAGS.values():
            self.assertNotContains(response, flag)

    def test_home_links_to_separate_flag_submit_page(self):
        response = self.client.get('/')

        self.assertContains(response, 'href="/flags/"')
        self.assertContains(response, '제출 페이지')
        self.assertNotContains(response, 'name="flag_1"')
        self.assertNotContains(response, 'name="flag_6"')

    def test_flag_submit_page_renders_six_flag_inputs(self):
        response = self.client.get('/flags/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '플래그 제출')
        self.assertContains(response, 'name="flag_1"')
        self.assertContains(response, 'name="flag_2"')
        self.assertContains(response, 'name="flag_3"')
        self.assertContains(response, 'name="flag_4"')
        self.assertContains(response, 'name="flag_5"')
        self.assertContains(response, 'name="flag_6"')
        self.assertNotContains(response, 'name="flag_7"')
        self.assertContains(response, '확인하기')

    def test_flag_submit_page_renders_separate_bonus_flag_input(self):
        response = self.client.get('/flags/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '보너스 플래그')
        self.assertContains(response, '보너스 페이지에서 받은 플래그')
        self.assertContains(response, 'action="/bonus/flag-check/"')
        self.assertContains(response, 'name="bonus_flag"')
        self.assertContains(response, '보너스 확인')
        self.assertContains(response, 'href="/bonus/vault/"')
        self.assertContains(response, '보너스 문제 열기')

    def test_flag_checker_counts_unique_correct_flags_from_six_inputs(self):
        response = self.client.post('/flags/check/', {
            'flag_1': f' {TEST_FLAGS["html_comment"]} ',
            'flag_2': 'wrong-flag',
            'flag_3': TEST_FLAGS['sourcemap'],
            'flag_4': TEST_FLAGS['sourcemap'],
            'flag_5': '',
            'flag_6': TEST_FLAGS['idor'],
            'flag_7': TEST_FLAGS['localstorage_admin'],
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '정답 3개 / 6개')
        self.assertContains(response, '플래그 제출')
        self.assertContains(response, '입력한 6칸 중 중복을 제외하고 채점했습니다.')
        self.assertNotContains(response, f'value="{TEST_FLAGS["html_comment"]}"')
        self.assertNotContains(response, TEST_FLAGS['sourcemap'])
        self.assertNotContains(response, TEST_FLAGS['idor'])
        self.assertNotContains(response, '정답 4개 / 6개')

    def test_flag_checker_redirects_to_special_page_when_all_flags_are_correct(self):
        response = self.client.post('/flags/check/', ALL_FLAGS)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/flags/success/?access='))

        success_response = self.client.get(response['Location'])
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, '특별 페이지')
        self.assertContains(success_response, '모든 플래그를 확인했습니다')
        for flag in TEST_FLAGS.values():
            self.assertNotContains(success_response, flag)

    def test_special_page_blocks_direct_url_after_success_cookie_is_issued(self):
        response = self.client.post('/flags/check/', ALL_FLAGS)

        self.assertEqual(response.status_code, 302)

        direct_response = self.client.get('/flags/success/')
        self.assertEqual(direct_response.status_code, 302)
        self.assertEqual(direct_response['Location'], '/flags/')

    def test_special_page_access_link_is_single_use(self):
        response = self.client.post('/flags/check/', ALL_FLAGS)

        self.assertEqual(response.status_code, 302)

        success_response = self.client.get(response['Location'])
        self.assertEqual(success_response.status_code, 200)

        replay_response = self.client.get(response['Location'])
        self.assertEqual(replay_response.status_code, 302)
        self.assertEqual(replay_response['Location'], '/flags/')

    def test_special_page_requires_completed_flag_check(self):
        response = self.client.get('/flags/success/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/flags/')

    def test_flag_checker_source_uses_runtime_flag_store(self):
        flags_source = Path(__file__).resolve().parents[1].joinpath('flags.py').read_text(encoding='utf-8')

        for flag in TEST_FLAGS.values():
            self.assertNotIn(flag, flags_source)
        self.assertIn('get_all_flags', flags_source)

    def test_flag_checker_rate_limit_does_not_require_session_storage(self):
        common_source = (
            Path(__file__).resolve().parents[1]
            .joinpath('endpoints', 'common.py')
            .read_text(encoding='utf-8')
        )

        self.assertNotIn('request.session', common_source)
        self.assertIn('cache', common_source)

    def test_flag_checker_rate_limits_repeated_attempts(self):
        payload = {
            'flag_1': 'wrong-flag',
            'flag_2': '',
            'flag_3': '',
            'flag_4': '',
            'flag_5': '',
            'flag_6': '',
        }

        for _ in range(10):
            response = self.client.post('/flags/check/', payload)
            self.assertEqual(response.status_code, 200)

        response = self.client.post('/flags/check/', payload)

        self.assertEqual(response.status_code, 429)
        self.assertContains(response, '시도가 너무 많습니다.', status_code=429)
        self.assertNotContains(response, '정답 0개 / 6개', status_code=429)
