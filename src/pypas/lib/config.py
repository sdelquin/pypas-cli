from pathlib import Path
from typing import Any

import toml
from pypas import console, settings


class Config:
    def __init__(self, path: Path = settings.MAIN_CONFIG_FILE):
        self.path = path
        if not self.path.exists():
            console.print(f'Config file has been created: [note]{self.path}')
            self.path.touch()
            self.just_created = True
        else:
            self.just_created = False

        self.data = self.load()

    def load(self) -> dict:
        with open(self.path) as f:
            return toml.load(f)

    def save(self) -> None:
        if not self.just_created:
            console.print(f'Config file has been updated: [note]{self.path}')
        with open(self.path, 'w') as f:
            toml.dump(self.data, f)

    def __setitem__(self, name: str, value: Any) -> None:
        self.data[name] = value

    def __getitem__(self, name) -> object:
        return self.data[name]

    def has_token(self) -> bool:
        return 'token' in self.data
