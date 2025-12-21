from pathlib import Path
from urllib.parse import urljoin

from prettyconf import config

PYPAS_BASE_URL = config('PYPAS_BASE_URL', default='https://pypas.es/')
PYPAS_AUTH_URLPATH = urljoin(PYPAS_BASE_URL, '/access/auth/')
PYPAS_GET_EXERCISE_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/get/{exercise_slug}/')
PYPAS_PUT_ASSIGNMENT_URLPATH = urljoin(PYPAS_BASE_URL, '/assignments/put/{exercise_slug}/')
PYPAS_LOG_URLPATH = urljoin(PYPAS_BASE_URL, '/assignments/log/')
PYPAS_LIST_EXERCISES_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/list/')
PYPAS_PULL_URLPATH = urljoin(PYPAS_BASE_URL, '/assignments/pull/{item_slug}/')
PYPAS_EXERCISE_INFO_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/info/{exercise_slug}/')

EXERCISE_CONFIG_FILE = config('EXERCISE_CONFIG_FILE', default='.pypas.toml')
MAIN_CONFIG_FILE = config('MAIN_CONFIG_FILE', default=Path.home() / '.pypas.toml', cast=Path)
LARGE_FILE_SIZE = config('LARGE_FILE_SIZE', default=1024 * 1024, cast=int)

PYPAS_SKIP_VERSION_CHECK_VAR = config(
    'PYPAS_SKIP_VERSION_CHECK_VAR', default='PYPAS_SKIP_VERSION_CHECK'
)

DEFAULT_EXERCISE_VERSION = config('DEFAULT_EXERCISE_VERSION', default='0.1.0')
