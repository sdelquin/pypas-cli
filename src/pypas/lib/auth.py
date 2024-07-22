from urllib.parse import urljoin

import requests
from pypas import settings

from .console import console


class User:
    def __init__(self, token: str):
        self.token = token
        self.auth_url = urljoin(settings.PYPAS_AUTH_URLPATH, token + '/')

    def authenticate(self) -> bool:
        with console.status(f'[dim]Authenticating user at: [italic]{self.auth_url}'):
            try:
                response = requests.get(self.auth_url)
                response.raise_for_status()
            except Exception as err:
                console.error(err)
                return False
            if (data := response.json())['success']:
                console.success(
                    f'Congratulations [i]{data["payload"]}[/i]. You have been successfully authenticated'
                )
                return True
            else:
                console.error(data['payload'])
                return False
