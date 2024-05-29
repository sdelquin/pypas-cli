from http import HTTPStatus
from urllib.parse import urljoin

import requests
from pypas import settings

from .console import console


class User:
    def __init__(self, token: str):
        self.token = token
        self.token_validation_url = urljoin(settings.PYPAS_VALIDATE_URLPATH, token + '/')

    def authenticate(self) -> bool:
        console.debug(f'Authenticating user at: [i]{self.token_validation_url}', end=' ')
        response = requests.get(self.token_validation_url)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            console.check()
            console.success(
                f'Congratulations [i]{data['name']}[/i]. You have been successfully authenticated'
            )
            return True
        else:
            console.fail()
            console.error('User cannot be authenticated')
            console.debug('Check the access token with the administrator')
            return False
