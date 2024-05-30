from urllib.parse import urljoin

import requests
from pypas import settings

from .console import console


class User:
    def __init__(self, token: str):
        self.token = token
        self.auth_url = urljoin(settings.PYPAS_AUTH_URLPATH, token + '/')

    def authenticate(self) -> bool:
        console.debug(f'Authenticating user at: [i]{self.auth_url}', cr=False)
        response = requests.get(self.auth_url)
        try:
            response.raise_for_status()
        except Exception as err:
            console.fail()
            console.error(err)
            return False
        if (data := response.json())['success']:
            console.check()
            console.success(
                f'Congratulations [i]{data["payload"]}[/i]. You have been successfully authenticated'
            )
            return True
        else:
            console.fail()
            console.error(data['payload'])
            return False
