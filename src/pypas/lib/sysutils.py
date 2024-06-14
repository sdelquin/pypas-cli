import shlex
import subprocess
import sys
from pathlib import Path
from sys import platform

import pkg_resources


class OS:
    LINUX = 1
    MACOS = 2
    WINDOWS = 3
    OTHER = 4


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
    subprocess.check_call(cmd)


def get_pypas_version():
    dist = pkg_resources.get_distribution('pypas-cli')
    return f'{dist.key} {dist.version} from {dist.location}'


def get_file_size(path: Path) -> tuple[int, str]:
    KB = 1024
    MB = 1024 * 1024

    size = path.stat().st_size
    if size < KB:
        usize = size
        unit = 'B'
    elif KB < size < MB:
        usize = size / KB
        unit = 'KB'
    else:
        usize = size / MB
        unit = 'MB'
    return size, f'{usize:.1f} {unit}'
