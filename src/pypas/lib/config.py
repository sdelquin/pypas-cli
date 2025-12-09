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

    @staticmethod
    def unauth():
        settings.MAIN_CONFIG_FILE.unlink(missing_ok=True)

    @staticmethod
    def find_nested_config(
        config_file: str = settings.EXERCISE_CONFIG_FILE, relative_to_cwd: bool = False
    ) -> Path | None:
        base = Path('.').resolve()
        for path in base.rglob(config_file):
            if (p := path.parent) != base:
                return p if not relative_to_cwd else p.relative_to(base)
        return None

    @staticmethod
    def local_config_exists(
        config_file: str = settings.EXERCISE_CONFIG_FILE, ignore_main_config: bool = False
    ) -> bool:
        return Path(config_file).exists() and (
            ignore_main_config or Path('.').resolve() != settings.MAIN_CONFIG_FILE.parent.resolve()
        )
