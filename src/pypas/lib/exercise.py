from __future__ import annotations

import os
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import tomllib
from pypas import settings

from . import utils
from .console import console


class Exercise:
    def __init__(self, exercise_slug: str):
        self.slug = exercise_slug
        self.url = urljoin(settings.PYPAS_EXERCISES_URLPATH, exercise_slug + '/')

    @property
    def zipname(self) -> str:
        return f'{self.slug}.zip'

    @property
    def folder(self) -> Path:
        return Path(self.slug)

    @property
    def cwd_folder(self) -> str:
        return f'./{self.folder}'

    @property
    def config(self) -> dict:
        if not getattr(self, '_cfg', None) or not self._cfg:  # type: ignore
            self._cfg = Exercise.load_config()
        return self._cfg

    def folder_exists(self) -> bool:
        return self.folder.exists()

    def download(self) -> Path | None:
        console.print(f'Getting exercise from: [italic]{self.url}')
        if downloaded_zip := utils.download(self.url, self.zipname, save_temp=True):
            self.downloaded_zip = downloaded_zip
        return downloaded_zip

    def unzip(self):
        console.print('Inflating exercise bundle', end=' ')
        with zipfile.ZipFile(self.downloaded_zip) as zip_ref:
            zip_ref.extractall()
        console.print('✔', style='success')
        os.remove(self.downloaded_zip)

    def open_docs(self):
        os.system(f'{utils.get_open_cmd()} docs/README.pdf')

    @classmethod
    def from_config(cls) -> Exercise | None:
        try:
            return cls(Exercise.load_config()['slug'])
        except KeyError:
            console.print(
                f'Config file {settings.EXERCISE_CONFIG_FILE} is corrupt!', style='danger'
            )
            return None

    @staticmethod
    def load_config(filename: str = settings.EXERCISE_CONFIG_FILE):
        with open(filename, 'rb') as f:
            return tomllib.load(f)
