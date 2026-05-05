import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import override_settings


TEST_FLAGS = {
    'html_comment': 'TESTFLAG{html_comment}',
    'sourcemap': 'TESTFLAG{source_map}',
    'localstorage_admin': 'TESTFLAG{local_storage_admin}',
    'debug_api': 'TESTFLAG{debug_api}',
    'idor': 'TESTFLAG{idor}',
    'sqli': 'TESTFLAG{sqli}',
    'bonus': 'TESTFLAG{bonus_prize}',
}


class EncryptedFlagStoreMixin:
    def setUp(self):
        super().setUp()

        from challenges.flag_store import clear_flag_cache, write_encrypted_flag_db

        self._flag_tmpdir = TemporaryDirectory()
        self.addCleanup(self._flag_tmpdir.cleanup)

        self.flag_db_path = Path(self._flag_tmpdir.name).joinpath('flags.sqlite3')
        self.flag_db_password = 'test-db-password'
        self._flag_env = patch.dict(
            os.environ,
            {
                'CTF_FLAG_DB_PASSWORD': self.flag_db_password,
                'CTF_BONUS_TOKEN_KEY': 'test-bonus-token-key',
            },
        )
        self._flag_env.start()
        self.addCleanup(self._flag_env.stop)

        write_encrypted_flag_db(self.flag_db_path, self.flag_db_password, TEST_FLAGS)
        clear_flag_cache()
        self.addCleanup(clear_flag_cache)

        self._flag_settings = override_settings(CTF_FLAG_DB_PATH=self.flag_db_path)
        self._flag_settings.enable()
        self.addCleanup(self._flag_settings.disable)
