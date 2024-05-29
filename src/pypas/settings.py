from pathlib import Path
from urllib.parse import urljoin

from prettyconf import config

PYPAS_BASE_URL = config('PYPAS_BASE_URL', default='https://pypas.es/')
PYPAS_EXERCISES_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/')
PYPAS_VALIDATE_URLPATH = urljoin(PYPAS_BASE_URL, '/access/auth/')

EXERCISE_CONFIG_FILE = config('EXERCISE_CONFIG_FILE', default='.pypas.toml')
MAIN_CONFIG_FILE = config('MAIN_CONFIG_FILE', default=Path.home() / '.pypas.toml', cast=Path)
