from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import toml
from pypas import settings

from . import network, sysutils
from .console import CustomTable, console


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
    def files(self):
        for item in Path('.').glob('**/*'):
            if item.is_file():
                yield item

    def folder_exists(self) -> bool:
        return self.folder.exists()

    def download(self):
        url = settings.PYPAS_GET_EXERCISE_URLPATH.format(exercise_slug=self.slug)
        console.debug(f'Getting exercise from: [italic]{url}')
        if monad := network.download(url, self.zipname, save_temp=True):
            self.downloaded_zip = monad.payload
            return self.downloaded_zip
        else:
            console.error(monad.payload)
            return None

    def zip(self, to_tmp_dir: bool = False, verbose: bool = False) -> Path:
        console.info('Compressing exercise contents', cr=verbose)
        zip_path = tempfile.mkstemp(suffix='.zip')[1] if to_tmp_dir else self.zipname
        zip_file = Path(zip_path)
        with zipfile.ZipFile(zip_file, 'w') as archive:
            for file in self.files:
                if file.name == self.zipname:
                    continue
                if verbose:
                    console.debug(file)
                archive.write(file)
        if not verbose:
            console.check()
        return zip_file

    def unzip(self, to_tmp_dir: bool = False) -> Path:
        tmp_dir = tempfile.mkdtemp()
        target_dir = Path(tmp_dir) if to_tmp_dir else self.folder
        console.info('Inflating exercise bundle', cr=False)
        with zipfile.ZipFile(self.downloaded_zip) as zip_ref:
            zip_ref.extractall(target_dir)
        console.check()
        os.remove(self.downloaded_zip)
        return target_dir

    def open_docs(self):
        os.system(f'{sysutils.get_open_cmd()} docs/README.pdf')

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
        if monad := network.upload(
            url, fields=dict(token=token), filepath=zipfile, filename=self.zipname
        ):
            console.success(monad.payload)
        else:
            console.error(monad.payload)
        zipfile.unlink(missing_ok=True)

    def test(self):
        subprocess.run('pytest')

    @classmethod
    def from_config(cls) -> Exercise:
        return cls(Exercise.load_config()['slug'])

    @staticmethod
    def load_config(filename: str = settings.EXERCISE_CONFIG_FILE):
        with open(filename) as f:
            return toml.load(f)

    @staticmethod
    def pytest_help():
        console.info('[note]pypas test[/note] is just a wrapper for [note]pytest[/note]')
        console.info(
            'You can find documentation on how to invoke pytest at: [warning]https://docs.pytest.org/en/latest/how-to/usage.html'
        )
        console.debug('Here you have some of the more useful options:')

        table = CustomTable(('Command', 'quote'), ('Description', ''))
        table.add_row('pytest -x', 'Exit instantly on first error or failed test.')
        table.add_row(
            'pytest -k <expression>',
            'Only run tests which match the given substring expression.',
        )
        table.add_row('pytest -v', 'Increase verbosity.')
        table.add_row('pytest -q', 'Decrease verbosity.')
        table.add_row('pytest --lf', 'Rerun only the tests that failed at the last run.')
        table.add_row(
            'pytest --sw',
            'Exit on test failure and continue from last failing test next time.',
        )
        table.add_row('pytest <path/to>::<test>', 'Run specific test.')
        console.print(table)

    def __str__(self):
        return self.slug
