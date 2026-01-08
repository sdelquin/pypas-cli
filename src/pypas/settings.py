from pathlib import Path
from urllib.parse import urljoin

from prettyconf import config

PYPAS_BASE_URL = config('PYPAS_BASE_URL', default='https://pypas.es/')
PYPAS_AUTH_URL = urljoin(PYPAS_BASE_URL, '/access/auth/{token}/')
PYPAS_AUTH_INFO_URL = urljoin(PYPAS_BASE_URL, '/access/info/{token}/')
PYPAS_GET_EXERCISE_URL = urljoin(PYPAS_BASE_URL, '/exercises/get/{exercise_slug}/')
PYPAS_PUT_ASSIGNMENT_URL = urljoin(PYPAS_BASE_URL, '/assignments/put/{exercise_slug}/')
PYPAS_LOG_URL = urljoin(PYPAS_BASE_URL, '/assignments/log/')
PYPAS_LIST_EXERCISES_URL = urljoin(PYPAS_BASE_URL, '/exercises/list/')
PYPAS_PULL_URL = urljoin(PYPAS_BASE_URL, '/assignments/pull/{item_slug}/')
PYPAS_EXERCISE_INFO_URL = urljoin(PYPAS_BASE_URL, '/exercises/info/{exercise_slug}/')

EXERCISE_CONFIG_FILE = config('EXERCISE_CONFIG_FILE', default='.pypas.toml')
MAIN_CONFIG_FILE = config('MAIN_CONFIG_FILE', default=Path.home() / '.pypas.toml', cast=Path)
LARGE_FILE_SIZE = config('LARGE_FILE_SIZE', default=1024 * 1024, cast=int)

PYPAS_SKIP_VERSION_CHECK_VAR = config(
    'PYPAS_SKIP_VERSION_CHECK_VAR', default='PYPAS_SKIP_VERSION_CHECK'
)

DEFAULT_EXERCISE_VERSION = config('DEFAULT_EXERCISE_VERSION', default='0.1.0')

PYPAS_DOCS_URL = 'https://aprendepython.es/third-party/learning/pypas/'
PYPAS_DOCS_UPGRADE_URL = urljoin(PYPAS_DOCS_URL, '#upgrade')
PYPAS_DOCS_UPDATE_URL = urljoin(PYPAS_DOCS_URL, '#update')
