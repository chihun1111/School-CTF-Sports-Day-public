from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings

from .utils import TEST_FLAGS


class EncryptedFlagStoreTests(TestCase):
    def test_encrypted_flag_db_round_trips_without_plaintext(self):
        from challenges.flag_store import load_encrypted_flags, write_encrypted_flag_db

        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir).joinpath('flags.sqlite3')
            write_encrypted_flag_db(db_path, 'password-for-test', TEST_FLAGS)

            db_bytes = db_path.read_bytes()

            for flag in TEST_FLAGS.values():
                self.assertNotIn(flag.encode('utf-8'), db_bytes)
            self.assertEqual(
                load_encrypted_flags(db_path, 'password-for-test'),
                TEST_FLAGS,
            )

    @override_settings(CTF_FLAG_DB_PATH=Path('/missing/flags.sqlite3'))
    def test_missing_runtime_flag_db_is_configuration_error(self):
        from django.core.exceptions import ImproperlyConfigured

        from challenges.flag_store import clear_flag_cache, get_flag

        clear_flag_cache()

        with self.assertRaises(ImproperlyConfigured):
            get_flag('html_comment')

    def test_source_tree_does_not_contain_plaintext_production_flags(self):
        pattern = 'KDUCTF' + '{'
        project_root = Path(__file__).resolve().parents[3]
        excluded_parts = {
            '.git',
            '.venv',
            '__pycache__',
            'db.sqlite3',
            'private',
            'staticfiles',
        }
        text_suffixes = {
            '.css',
            '.html',
            '.js',
            '.json',
            '.md',
            '.py',
            '.txt',
        }
        leaks = []

        for path in project_root.rglob('*'):
            if not path.is_file():
                continue
            if any(part in excluded_parts for part in path.parts):
                continue
            if path.suffix not in text_suffixes:
                continue
            if pattern in path.read_text(encoding='utf-8'):
                leaks.append(path.relative_to(project_root).as_posix())

        self.assertEqual(leaks, [])
