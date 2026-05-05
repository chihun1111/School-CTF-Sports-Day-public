import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from challenges.flag_store import SECRET_NAMES, clear_flag_cache, write_encrypted_flag_db


ENV_BY_SECRET = {
    'html_comment': 'CTF_FLAG_HTML_COMMENT',
    'sourcemap': 'CTF_FLAG_SOURCEMAP',
    'localstorage_admin': 'CTF_FLAG_LOCALSTORAGE_ADMIN',
    'debug_api': 'CTF_FLAG_DEBUG_API',
    'idor': 'CTF_FLAG_IDOR',
    'sqli': 'CTF_FLAG_SQLI',
}


class Command(BaseCommand):
    help = 'Create or replace the encrypted CTF flag database from environment variables.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--db-path',
            default=settings.CTF_FLAG_DB_PATH,
            help='Encrypted flag DB path. Defaults to CTF_FLAG_DB_PATH.',
        )

    def handle(self, *args, **options):
        password = os.environ.get('CTF_FLAG_DB_PASSWORD')
        if not password:
            raise CommandError('CTF_FLAG_DB_PASSWORD is required.')

        flags = {
            name: os.environ.get(env_name, '')
            for name, env_name in ENV_BY_SECRET.items()
        }
        missing = [
            ENV_BY_SECRET[name]
            for name in SECRET_NAMES
            if not flags.get(name)
        ]
        if missing:
            raise CommandError(
                'Missing flag environment variables: ' + ', '.join(missing)
            )

        write_encrypted_flag_db(options['db_path'], password, flags)
        clear_flag_cache()
        self.stdout.write(self.style.SUCCESS(f'Encrypted flag DB written to {options["db_path"]}'))
