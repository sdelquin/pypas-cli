from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from textwrap import dedent
from typing import List

import pathspec
import pytest
import toml
from rich.panel import Panel

from pypas import settings

from . import network, sysutils
from .console import CustomTable, console


class Exercise:
    def __init__(self, exercise_slug: str):
        self.slug = exercise_slug
        self._latest_version = None

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

    def download(self, token: str):
        url = settings.PYPAS_GET_EXERCISE_URLPATH.format(exercise_slug=self.slug)
        console.debug(f'Getting exercise from: [italic]{url}')
        if monad := network.download(url, dict(token=token), self.zipname, save_temp=True):
            self.downloaded_zip = monad.payload
            return self.downloaded_zip
        else:
            console.error(monad.payload)
            return None

    def zip(self, to_tmp_dir: bool = False, verbose: bool = False) -> Path:
        console.info('Compressing exercise contents', cr=verbose)
        exclude_patterns = pathspec.PathSpec.from_lines(
            'gitwildmatch', self.config.get('exclude_from_zip', [])
        )
        zip_path = tempfile.mkstemp(suffix='.zip')[1] if to_tmp_dir else self.zipname
        zip_file = Path(zip_path)
        with zipfile.ZipFile(zip_file, 'w') as archive:
            for file in self.files:
                if file.name == self.zipname:
                    continue
                if exclude_patterns.match_file(str(file)):
                    if verbose:
                        console.warning(f'Ignoring {file}')
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
        try:
            self.downloaded_zip.unlink(missing_ok=True)
        except PermissionError:
            # Windows issue
            console.debug(f"Temporary file couldn't been removed: '{self.downloaded_zip}'")
        return target_dir

    def open_docs(self):
        os.system(f'{sysutils.get_open_cmd()} docs/README.pdf')

    def update(self, src_dir: Path, backup: bool = True):
        backup_files = pathspec.PathSpec.from_lines(
            'gitwildmatch', self.config.get('backup_on_update', [])
        )
        for dirpath, dirs, files in os.walk(src_dir):
            for filename in files:
                incoming_file = Path(dirpath) / filename
                current_file = incoming_file.relative_to(src_dir)
                if current_file.exists():
                    if filecmp.cmp(current_file, incoming_file, shallow=False):
                        continue
                    console.info(f'[highlight][U][/highlight] {current_file}', cr=False)
                    if backup:
                        if backup_files.match_file(str(current_file)):
                            backup_file = current_file.with_suffix(current_file.suffix + '.bak')
                            console.debug(f' (Backup {current_file} → {backup_file})', cr=False)
                            shutil.copy(current_file, backup_file)
                    console.info('')
                else:
                    console.info(f'[highlight][A][/highlight] {current_file}')
                current_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(incoming_file, current_file)
        shutil.rmtree(src_dir, ignore_errors=True)
        console.success(
            f'Updated [i]{self}[/i] from [note]{self.version}[/note] to [note]{self.latest_version}[/note]',
            emphasis=True,
        )

    def upload(self, zipfile: Path, token: str):
        if self.check_zipfile_size(zipfile):
            url = settings.PYPAS_PUT_ASSIGNMENT_URLPATH.format(exercise_slug=self.slug)
            console.debug(f'Uploading exercise to: [italic]{url}')
            if monad := network.upload(
                url, fields=dict(token=token), filepath=zipfile, filename=self.zipname
            ):
                console.success('Exercise was sucessfully uploaded')
                console.debug(monad.payload)
            else:
                console.error(monad.payload)
            zipfile.unlink(missing_ok=True)

    def test(self, args: List[str]):
        if test_cmd := self.config.get('test_cmd'):
            test_cmd = f'{test_cmd} {" ".join(args)}' if args else test_cmd
            console.info(f'Running tests with: [note]{test_cmd}[/note]')
            subprocess.run(test_cmd, shell=True)
        else:
            pytest.main(args=args)

    @classmethod
    def from_config(cls) -> Exercise:
        return cls(Exercise.load_config()['slug'])

    @staticmethod
    def load_config(filename: str = settings.EXERCISE_CONFIG_FILE):
        with open(filename) as f:
            return toml.load(f)

    @staticmethod
    def check_zipfile_size(zipfile: Path, limit=settings.LARGE_FILE_SIZE) -> bool:
        console.info('Checking file size', cr=False)
        size, str_size = sysutils.get_file_size(zipfile)
        if size > limit:
            console.fail()
            console.error(f'Aborting: zipfile is too large → {str_size}')
            console.warning('Check contents (hidden files) or contact with administrator.')
            return False
        else:
            console.check()
            return True

    @staticmethod
    def log(token: str, frame_ref: str, verbose: bool = False) -> None:
        url = settings.PYPAS_LOG_URLPATH
        with console.status(f'[dim]Getting log from: [italic]{url}'):
            payload = dict(token=token, frame=frame_ref, verbose=verbose)
            if monad := network.post(url, payload):
                console.warning('[dim i]Listing assignments only from [b]active[/b] frames...')
                if monad.payload:
                    for frame in monad.payload:
                        console.print(Panel(frame['name'], expand=False, style='bold bright_green'))
                        console.debug(f' └ Frame slug: [bright_green]{frame["slug"]}')
                        table = CustomTable(
                            'Uploaded',
                            ('Passed', 'success'),
                            ('Failed', 'error'),
                            ('Waiting', 'dim cyan'),
                            ('Score', 'note'),
                        )
                        try:
                            score = frame['passed'] / frame['available'] * 10
                        except ZeroDivisionError:
                            score = 0
                        table.add_row(
                            f'{frame["uploaded"]}/{frame["available"]}',
                            str(frame['passed']),
                            str(frame['failed']),
                            str(frame['waiting']),
                            f'{score:.02f}',
                        )
                        console.print(table)
                        if verbose:
                            for assignment in frame['assignments']:
                                msg = f'· {assignment["slug"]}'
                                match assignment['passed']:
                                    case True:
                                        console.check(msg)
                                    case False:
                                        console.fail(msg)
                                    case _:
                                        console.debug(msg)
                else:
                    console.warning("There's no assignments with the given criteria")
            else:
                console.error(monad.payload)

    @classmethod
    def list(cls, token: str, frame_ref: str, primary_topic: str, secondary_topic: str):
        url = settings.PYPAS_LIST_EXERCISES_URLPATH
        with console.status(f'[dim]Getting exercise list from: [italic]{url}'):
            payload = dict(
                token=token,
                frame=frame_ref,
                primary_topic=primary_topic,
                secondary_topic=secondary_topic,
            )
            if monad := network.post(url, payload):
                console.warning('[dim i]Listing exercises only from [b]active[/b] frames...')
                if monad.payload:
                    for frame in monad.payload:
                        console.print(Panel(frame['name'], expand=False, style='bold bright_green'))
                        console.debug(f' └ Frame slug: [bright_green]{frame["slug"]}')
                        if frame['exercises']:
                            table = CustomTable('Exercise', ('Topic', 'magenta'))
                            for exercise in frame['exercises']:
                                table.add_row(exercise['slug'], exercise['topic'])
                            console.print(table)
                        else:
                            console.warning(
                                "There's no exercises in this frame with the given criteria"
                            )
            else:
                console.error(monad.payload)

    def run(self):
        sysutils.run_python_file()

    def __str__(self):
        return self.slug

    @staticmethod
    def pull(item_slug: str, token: str) -> Path | None:
        url = settings.PYPAS_PULL_URLPATH.format(item_slug=item_slug)
        console.debug(f'Pulling items from: [italic]{url}')
        if monad := network.download(url, dict(token=token), f'{item_slug}.zip', save_temp=True):
            return monad.payload
        else:
            console.error(monad.payload)
            return None

    @property
    def latest_version(self) -> str | None:
        if self._latest_version:
            return self._latest_version
        url = settings.PYPAS_EXERCISE_INFO_URLPATH.format(exercise_slug=self.slug)
        if monad := network.get(url):
            self._latest_version = monad.payload.get('version')
            return self._latest_version
        else:
            console.error(monad.payload)
            return None

    @property
    def version(self) -> str:
        return str(self.config.get('version', settings.DEFAULT_EXERCISE_VERSION))

    def is_up_to_date(self) -> bool:
        latest_version = self.latest_version
        current_version = self.version
        return latest_version == current_version

    def handle_exercise_version(
        self,
        confirm: bool = False,
        confirm_suffix: str = '',
        env_var: str = settings.PYPAS_SKIP_VERSION_CHECK_VAR,
    ) -> bool:
        """Check if there's a new version of the exercise available.
        Returns True if the user wants to continue with the old version.
        """
        if os.environ.get(env_var) == '1':
            return True
        latest_version = self.latest_version
        current_version = self.version
        if latest_version and current_version and latest_version != current_version:
            console.warning(
                dedent(f"""
                A new version of [bold]{self.slug}[/bold] is available: [note]{latest_version}[/note] (you have [note]{current_version}[/note])
                You'll probably get errors if you continue using an old version.
                Run [note]pypas update[/note] to update to the latest version [dim](https://pypas.es/docs/#actualizar-un-ejercicio)[/dim].
                [quote][dim]If you want to disable this warning, set an environment variable: [note]{env_var}=1[/note][/quote][/dim]
            """)
            )
            if confirm:
                confirm_suffix = f' {confirm_suffix}' if not confirm_suffix.startswith(' ') else ''
                return console.confirm(f'Continue{confirm_suffix}?')
        return True
