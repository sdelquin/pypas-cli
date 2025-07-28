import shlex
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from sys import platform

from pypas import console


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


def upgrade_pypas() -> bool:
    UPGRADE_COMMANDS = [
        'uv tool upgrade --no-cache pypas-cli',
        f'{sys.executable} -m pip install -q --no-cache -U pypas-cli',
        'pipx upgrade pypas-cli',
    ]
    for cmd in UPGRADE_COMMANDS:
        try:
            console.debug(cmd, cr=False)
            subprocess.run(shlex.split(cmd), capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            console.fail()
        else:
            console.check()
            return True
    return False


def get_package_info(package: str = 'pypas-cli') -> str:
    try:
        dist = distribution(package)
        name = dist.metadata['Name']
        version = dist.version
        location = dist.locate_file('')
        return f'Package: {name}\nVersion: {version}\nPath: {location}'
    except PackageNotFoundError:
        return "Package '{package}' is not already installed."


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


def run_python_file(file='main.py'):
    cmd = f'{sys.executable} {file}'
    subprocess.run(shlex.split(cmd))
