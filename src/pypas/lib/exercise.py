from __future__ import annotations

import os
import shutil
import tempfile
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

    def unzip(self, to_tmp_dir: bool = False) -> Path:
        tmp_dir = tempfile.TemporaryDirectory(delete=False)
        target_dir = Path(tmp_dir.name) if to_tmp_dir else self.folder
        console.print('Inflating exercise bundle', end=' ')
        with zipfile.ZipFile(self.downloaded_zip) as zip_ref:
            zip_ref.extractall(target_dir)
        console.done()
        os.remove(self.downloaded_zip)
        return target_dir

    def open_docs(self):
        os.system(f'{utils.get_open_cmd()} docs/README.pdf')

    def update(self, src_dir: Path, backup: bool = True):
        for file in src_dir.glob('**/*'):
            if file.is_file():
                rel_file = file.relative_to(src_dir)
                if backup and rel_file.exists() and str(rel_file) in self.config['todo']:
                    backup_file = rel_file.with_suffix(rel_file.suffix + '.bak')
                    console.print(f'Backup {rel_file} → {backup_file}', end=' ')
                    shutil.copy(rel_file, backup_file)
                    console.done()
                rel_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file, rel_file)
        shutil.rmtree(src_dir, ignore_errors=True)
        console.great('Exercise is updated to last version!')

    @classmethod
    def from_config(cls) -> Exercise:
        return cls(Exercise.load_config()['slug'])

    @staticmethod
    def load_config(filename: str = settings.EXERCISE_CONFIG_FILE):
        with open(filename, 'rb') as f:
            return tomllib.load(f)
