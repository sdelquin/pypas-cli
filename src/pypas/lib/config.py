from pathlib import Path
from typing import Any

import toml
from pypas import console, settings


class Config:
    def __init__(self, path: Path = settings.MAIN_CONFIG_FILE):
        self.path = path
        if not self.path.exists():
            self.path.touch()
        self.data = self.load()

    def load(self) -> dict:
        with open(self.path) as f:
            return toml.load(f)

    def save(self) -> None:
        console.print(f'[dim]Config file has been updated: {self.path}')
        with open(self.path, 'w') as f:
            toml.dump(self.data, f)

    def __setitem__(self, name: str, value: Any) -> None:
        self.data[name] = value


config = Config()
