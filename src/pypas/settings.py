from urllib.parse import urljoin

from prettyconf import config

PYPAS_BASE_URL = config('PYPAS_BASE_URL', default='https://pypas.es/')
PYPAS_EXERCISES_URLPATH = urljoin(PYPAS_BASE_URL, '/exercises/')
