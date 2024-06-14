from pathlib import Path
from urllib.parse import urljoin

from prettyconf import config

PYPAS_BASE_URL = config('PYPAS_BASE_URL', default='https://pypas.es/')
PYPAS_AUTH_URLPATH = urljoin(PYPAS_BASE_URL, '/access/auth/')
PYPAS_GET_EXERCISE_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/{exercise_slug}/get/')
PYPAS_PUT_ASSIGNMENT_URLPATH = urljoin(PYPAS_BASE_URL, '/assignments/{exercise_slug}/put/')
PYPAS_STATS_URLPATH = urljoin(PYPAS_BASE_URL, '/assignments/stats/')

EXERCISE_CONFIG_FILE = config('EXERCISE_CONFIG_FILE', default='.pypas.toml')
MAIN_CONFIG_FILE = config('MAIN_CONFIG_FILE', default=Path.home() / '.pypas.toml', cast=Path)
LARGE_FILE_SIZE = config('LARGE_FILE_SIZE', default=1024 * 1024, cast=int)
ZIP_IGNORED_PATTERNS = config(
    'ZIP_IGNORED_PATTERNS', default='cache,node_modules', cast=config.list
)
ZIP_IGNORED_PATTERNS_RE = '|'.join(ZIP_IGNORED_PATTERNS)
