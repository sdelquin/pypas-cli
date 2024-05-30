from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import toml
from pypas import settings

from . import network, utils
from .console import console


class Exercise:
    def __init__(self, exercise_slug: str):
        self.slug = exercise_slug

    @property
    def zipname(self) -> str:
        return f'{self.slug}.zip'

    @property
    def folder(self) -> Path:
        return Path(self.slug)

    @property
    def config(self) -> dict:
        if not getattr(self, '_cfg', None) or not self._cfg:  # type: ignore
            self._cfg = Exercise.load_config()
        return self._cfg

    @property
    def contents(self):
        for item in Path('.').glob('**/*'):
            if item.is_file():
                yield item

    def folder_exists(self) -> bool:
        return self.folder.exists()

    def download(self) -> Path | None:
        url = settings.PYPAS_GET_EXERCISE_URLPATH.format(exercise_slug=self.slug)
        console.debug(f'Getting exercise from: [italic]{url}')
        if downloaded_zip := network.download(url, self.zipname, save_temp=True):
            self.downloaded_zip = downloaded_zip
        return downloaded_zip

    def zip(self, to_tmp_dir: bool = False, verbose: bool = False) -> Path:
        console.print('Compressing exercise contents', end='\n' if verbose else ' ')
        zip_path = tempfile.mkstemp(suffix='.zip')[1] if to_tmp_dir else self.zipname
        zip_file = Path(zip_path)
        with zipfile.ZipFile(zip_file, 'w') as archive:
            for f in self.contents:
                if f.name == self.zipname:
                    continue
                if verbose:
                    console.debug(f)
                archive.write(f)
        zip_size = round(zip_file.stat().st_size / 1024)
        if verbose:
            console.print(
                f'Compressed exercise is available at: [note]{zip_file}[/note] [dim]({zip_size} kB)'
            )
        else:
            console.check()
        return zip_file

    def unzip(self, to_tmp_dir: bool = False) -> Path:
        tmp_dir = tempfile.mkdtemp()
        target_dir = Path(tmp_dir) if to_tmp_dir else self.folder
        console.print('Inflating exercise bundle', end=' ')
        with zipfile.ZipFile(self.downloaded_zip) as zip_ref:
            zip_ref.extractall(target_dir)
        console.check()
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
                    console.debug(f'Backup {rel_file} → {backup_file}')
                    shutil.copy(rel_file, backup_file)
                rel_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file, rel_file)
        shutil.rmtree(src_dir, ignore_errors=True)
        console.success('Exercise has been updated to the last version')

    def upload(self, zipfile: Path, token: str):
        url = settings.PYPAS_PUT_EXERCISE_URLPATH.format(exercise_slug=self.slug)
        console.debug(f'Uploading exercise to: [italic]{url}')
        success, msg = network.upload(
            url, fields=dict(token=token), filepath=zipfile, filename=self.zipname
        )
        if success:
            console.success(msg)
        else:
            console.error(msg, emphasis=False)
        zipfile.unlink(missing_ok=True)

    @classmethod
    def from_config(cls) -> Exercise:
        return cls(Exercise.load_config()['slug'])

    @staticmethod
    def load_config(filename: str = settings.EXERCISE_CONFIG_FILE):
        with open(filename) as f:
            return toml.load(f)

    def __str__(self):
        return self.slug
