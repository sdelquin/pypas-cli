import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from sys import platform

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from .console import console


class OS:
    LINUX = 1
    MACOS = 2
    WINDOWS = 3
    OTHER = 4


def download(url: str, filename: str, save_temp=False, chunk_size=1024) -> Path | None:
    # https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51
    if save_temp:
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        target_file = tmp_file.name
    else:
        target_file = filename
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
    except Exception as err:
        console.error(err)
        return None
    with open(target_file, 'wb') as file, Progress(
        TextColumn('[bold blue]{task.fields[filename]}'),
        BarColumn(),
        '[progress.percentage]{task.percentage:>3.1f}%',
        '•',
        DownloadColumn(),
        '•',
        TransferSpeedColumn(),
        '•',
        TimeRemainingColumn(),
    ) as progress:
        total = int(resp.headers.get('content-length', 0))
        task_id = progress.add_task('download', filename=filename, total=total)
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            progress.update(task_id, advance=size)
    return Path(target_file)


def check_os() -> int:
    if platform.startswith('linux'):
        return OS.LINUX
    if platform == 'darwin':
        return OS.MACOS
    if platform == 'win32':
        return OS.WINDOWS
    return OS.OTHER


def get_open_cmd() -> str:
    match check_os():
        case OS.LINUX:
            return 'xdg-open'
        case OS.MACOS:
            return 'open'
        case OS.WINDOWS:
            return 'start'
        case _:
            return ''


def upgrade_pypas():
    args = '-m pip install --no-cache -U pypas-cli'
    cmd = [sys.executable] + shlex.split(args)
    subprocess.Popen(cmd)
