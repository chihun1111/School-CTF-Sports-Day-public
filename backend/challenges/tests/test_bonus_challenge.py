import base64
import struct

from django.core.cache import cache
from django.test import TestCase

from .utils import EncryptedFlagStoreMixin, TEST_FLAGS


SHA256_K = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
)


def _right_rotate(value, bits):
    return ((value >> bits) | (value << (32 - bits))) & 0xFFFFFFFF


def _sha256_padding(message_length):
    padding = b'\x80'
    padding += b'\x00' * ((56 - (message_length + 1) % 64) % 64)
    padding += (message_length * 8).to_bytes(8, 'big')
    return padding


def _sha256_compress(state, chunk):
    words = list(struct.unpack('>16L', chunk))
    for index in range(16, 64):
        s0 = (
            _right_rotate(words[index - 15], 7)
            ^ _right_rotate(words[index - 15], 18)
            ^ (words[index - 15] >> 3)
        )
        s1 = (
            _right_rotate(words[index - 2], 17)
            ^ _right_rotate(words[index - 2], 19)
            ^ (words[index - 2] >> 10)
        )
        words.append((words[index - 16] + s0 + words[index - 7] + s1) & 0xFFFFFFFF)

    a, b, c, d, e, f, g, h = state
    for index in range(64):
        s1 = _right_rotate(e, 6) ^ _right_rotate(e, 11) ^ _right_rotate(e, 25)
        ch = (e & f) ^ (~e & g)
        temp1 = (h + s1 + ch + SHA256_K[index] + words[index]) & 0xFFFFFFFF
        s0 = _right_rotate(a, 2) ^ _right_rotate(a, 13) ^ _right_rotate(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (s0 + maj) & 0xFFFFFFFF
        h = g
        g = f
        f = e
        e = (d + temp1) & 0xFFFFFFFF
        d = c
        c = b
        b = a
        a = (temp1 + temp2) & 0xFFFFFFFF

    return tuple((left + right) & 0xFFFFFFFF for left, right in zip(state, (a, b, c, d, e, f, g, h)))


def _sha256_length_extend(digest_hex, original_length, append_bytes):
    state = struct.unpack('>8L', bytes.fromhex(digest_hex))
    glue_padding = _sha256_padding(original_length)
    processed_length = original_length + len(glue_padding)
    forged_tail = append_bytes + _sha256_padding(processed_length + len(append_bytes))

    for offset in range(0, len(forged_tail), 64):
        state = _sha256_compress(state, forged_tail[offset:offset + 64])

    return ''.join(f'{word:08x}' for word in state), glue_padding + append_bytes


def _decode_payload(payload_segment):
    payload_segment += '=' * (-len(payload_segment) % 4)
    return base64.urlsafe_b64decode(payload_segment.encode('ascii'))


def _encode_payload(payload_bytes):
    return base64.urlsafe_b64encode(payload_bytes).decode('ascii').rstrip('=')


def forge_winner_token(token, secret_length):
    payload_segment, digest = token.split('.', 1)
    payload = _decode_payload(payload_segment)
    forged_digest, suffix = _sha256_length_extend(
        digest,
        secret_length + len(payload),
        b'&role=winner',
    )
    return f'{_encode_payload(payload + suffix)}.{forged_digest}'


class BonusChallengeTests(EncryptedFlagStoreMixin, TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_bonus_vault_issues_guest_token_cookie_without_displaying_payload(self):
        response = self.client.get('/bonus/vault/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '특별상 접수')
        self.assertContains(response, 'name="ticket"')
        self.assertIn('vault_ticket', response.cookies)
        self.assertNotContains(response, 'role=guest')
        self.assertNotContains(response, 'uid=student01')
        self.assertNotContains(response, response.cookies['vault_ticket'].value)
        self.assertContains(response, '<textarea', html=False)
        self.assertContains(response, '전체 확인 코드')
        self.assertNotContains(response, f'>{response.cookies["vault_ticket"].value}</textarea>')

    def test_guest_token_does_not_open_prize_page(self):
        from challenges.bonus_tokens import issue_guest_token

        response = self.client.post('/bonus/check/', {
            'token': issue_guest_token(),
        })

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '확인 대상이 아닙니다.', status_code=403)

    def test_payload_only_bonus_ticket_returns_format_error_without_echoing_value(self):
        payload_only_ticket = (
            'dWlkPXN0dWRlbnQwMSZzY29wZT1zcG9ydHMtZGF5JmV4cGlyZXM9'
            'MTc3Nzk3MDUzNCZyb2xlPXdpbm5lcn9pW9O2ada8ON++XX1df3NnbQ=='
        )

        response = self.client.post('/bonus/check/', {
            'ticket': payload_only_ticket,
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '확인 코드 형식이 맞지 않습니다.', status_code=400)
        self.assertNotContains(response, payload_only_ticket, status_code=400)

    def test_bonus_flag_input_redirects_to_prize_page(self):
        response = self.client.post('/bonus/flag-check/', {
            'bonus_flag': TEST_FLAGS['bonus'],
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/bonus/prize/?access='))

        prize_response = self.client.get(response['Location'])
        self.assertEqual(prize_response.status_code, 200)
        self.assertContains(prize_response, '특별상 페이지')
        self.assertContains(prize_response, '특별상은 딱 1명')
        self.assertContains(prize_response, TEST_FLAGS['bonus'])

    def test_wrong_bonus_flag_returns_submit_page_without_echoing_value(self):
        response = self.client.post('/bonus/flag-check/', {
            'bonus_flag': 'wrong-bonus-flag',
        })

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '보너스 플래그가 일치하지 않습니다.', status_code=403)
        self.assertContains(response, '보너스 플래그', status_code=403)
        self.assertNotContains(response, 'wrong-bonus-flag', status_code=403)

    def test_bonus_flag_input_rate_limits_repeated_attempts(self):
        for _ in range(10):
            response = self.client.post('/bonus/flag-check/', {
                'bonus_flag': 'wrong-bonus-flag',
            })
            self.assertEqual(response.status_code, 403)

        response = self.client.post('/bonus/flag-check/', {
            'bonus_flag': 'wrong-bonus-flag',
        })

        self.assertEqual(response.status_code, 429)
        self.assertContains(response, '시도가 너무 많습니다.', status_code=429)
        self.assertNotContains(response, 'wrong-bonus-flag', status_code=429)

    def test_length_extension_token_opens_prize_page(self):
        vault_response = self.client.get('/bonus/vault/')
        guest_token = vault_response.cookies['vault_ticket'].value

        forged_token = forge_winner_token(
            guest_token,
            len('test-bonus-token-key'),
        )
        response = self.client.post('/bonus/check/', {
            'ticket': forged_token,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/bonus/prize/?access='))

        prize_response = self.client.get(response['Location'])
        self.assertEqual(prize_response.status_code, 200)
        self.assertContains(prize_response, '특별상 페이지')
        self.assertContains(prize_response, TEST_FLAGS['bonus'])

    def test_bonus_prize_blocks_direct_url_after_success_cookie_is_issued(self):
        vault_response = self.client.get('/bonus/vault/')
        guest_token = vault_response.cookies['vault_ticket'].value
        forged_token = forge_winner_token(
            guest_token,
            len('test-bonus-token-key'),
        )
        response = self.client.post('/bonus/check/', {
            'ticket': forged_token,
        })

        self.assertEqual(response.status_code, 302)

        direct_response = self.client.get('/bonus/prize/')
        self.assertEqual(direct_response.status_code, 302)
        self.assertEqual(direct_response['Location'], '/bonus/vault/')

    def test_bonus_prize_access_link_is_single_use(self):
        vault_response = self.client.get('/bonus/vault/')
        guest_token = vault_response.cookies['vault_ticket'].value
        forged_token = forge_winner_token(
            guest_token,
            len('test-bonus-token-key'),
        )
        response = self.client.post('/bonus/check/', {
            'ticket': forged_token,
        })

        self.assertEqual(response.status_code, 302)

        prize_response = self.client.get(response['Location'])
        self.assertEqual(prize_response.status_code, 200)

        replay_response = self.client.get(response['Location'])
        self.assertEqual(replay_response.status_code, 302)
        self.assertEqual(replay_response['Location'], '/bonus/vault/')

    def test_bonus_prize_page_requires_completed_bonus_check(self):
        response = self.client.get('/bonus/prize/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/bonus/vault/')
