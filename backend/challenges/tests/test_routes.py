from django.test import TestCase

from .utils import EncryptedFlagStoreMixin


class ChallengeRouteTests(EncryptedFlagStoreMixin, TestCase):
    def test_document_service_aliases_are_available(self):
        aliases = [
            '/campus/festival/',
            '/clubs/security/',
            '/clubs/admin/',
            '/system/status/',
            '/student/assignments/',
            '/student/assignments/1/',
            '/community/board/',
            '/hints/',
            '/frontend-01-html-comment/',
            '/frontend-02-sourcemap/',
            '/frontend-03-localstorage-admin/',
            '/backend-01-debug-api/',
            '/backend-02-idor/',
            '/backend-03-sqli/',
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                self.assertEqual(self.client.get(alias).status_code, 200)
