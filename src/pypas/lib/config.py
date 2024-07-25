from pathlib import Path
from typing import Any

import toml
from pypas import console, settings


class Config:
    def __init__(self, path: Path = settings.MAIN_CONFIG_FILE):
        self.path = path
        self.load()

    def load(self) -> dict:
        try:
            with open(self.path) as f:
                self.data = toml.load(f)
        except FileNotFoundError:
            self.data = {}
        return self.data

    def save(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self[key] = value
        action = 'updated' if self.exists() else 'created'
        console.info(f'Config file has been {action}: [note]{self.path}')
        with open(self.path, 'w') as f:
            toml.dump(self.data, f)

    def __setitem__(self, name: str, value: Any) -> None:
        self.data[name] = value

    def __getitem__(self, name) -> object:
        return self.data[name]

    def get(self, name) -> object | None:
        return self.data.get(name)

    def has_token(self) -> bool:
        return 'token' in self.data

    def exists(self):
        return self.path.exists()
