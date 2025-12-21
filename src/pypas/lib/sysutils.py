import fnmatch
import os
import shlex
import subprocess
import sys
import zipfile
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from sys import platform
from textwrap import dedent

import requests

from pypas import console, settings


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


def get_package_data(package: str = 'pypas-cli') -> dict[str, str]:
    try:
        dist = distribution(package)
        return {
            'name': dist.metadata['Name'],
            'version': dist.version,
            'location': str(dist.locate_file('')),
        }
    except PackageNotFoundError:
        return {}


def show_package_info(package: str = 'pypas-cli') -> None:
    if data := get_package_data(package):
        console.print(
            dedent(f"""\
            Package: {data.get('name')}
            Version: [note]{data.get('version')}[/note]
            Path: {data.get('location')}\
        """)
        )
    else:
        console.error(f"Package '{package}' is not yet installed")


def get_latest_package_version(package: str = 'pypas-cli') -> str | None:
    try:
        response = requests.get(f'https://pypi.org/pypi/{package}/json', timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['info']['version']
    except (requests.RequestException, KeyError):
        return None


def handle_package_version(
    package: str = 'pypas-cli',
    confirm: bool = False,
    confirm_suffix: str = '',
    env_var: str = settings.PYPAS_SKIP_VERSION_CHECK_VAR,
) -> bool:
    """Check if there's a new version of the package available.
    Returns True if the user wants to continue with the old version."""
    if os.environ.get(env_var) == '1':
        return True
    latest_version = get_latest_package_version(package)
    package_data = get_package_data(package)
    current_version = package_data.get('version')
    # current_version = '0.0.0'  # Temporary hardcoded version for testing
    if latest_version and current_version and latest_version != current_version:
        console.warning(
            dedent(f"""
            A new version of [bold]pypas-cli[/bold] is available: [note]{latest_version}[/note] (you have [note]{current_version}[/note])
            You'll probably get errors if you continue using an old version.
            Run [note]pypas upgrade[/note] to upgrade to the latest version [dim](https://pypas.es/docs/#actualizacion)[/dim].
            [quote][dim]If you want to disable this warning, set an environment variable: [note]{env_var}=1[/note][/quote][/dim]
        """)
        )
        if confirm:
            confirm_suffix = f' {confirm_suffix}' if not confirm_suffix.startswith(' ') else ''
            return console.confirm(f'Continue{confirm_suffix}?')
    return True


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


def zip(path: Path, zipname: str, ignored_patterns: list[str] = []) -> Path:
    """Zip the contents of a directory, excluding specified patterns."""
    zip_path = path / zipname
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                if not any(fnmatch.fnmatch(file, pattern) for pattern in ignored_patterns):
                    file_path = Path(root) / file
                    zipf.write(file_path, file_path.relative_to(path))
    return zip_path


def unzip(zip_path: Path, extract_to: Path | None = None) -> Path:
    """Unzip a file to a specified directory or the current directory."""
    extract_to = extract_to or Path.cwd()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to


def handle_upgrade_pypas():
    DOCS_UPGRADE_URL = 'https://pypas.es/docs/#actualizacion'
    CHANGELOG_URL = 'https://github.com/sdelquin/pypas-cli/blob/main/CHANGELOG.md#{version}'

    latest_version = get_latest_package_version()
    package_data = get_package_data()
    current_version = package_data.get('version')
    # current_version = '0.0.0'  # Temporary hardcoded version for testing
    if latest_version and current_version:
        if latest_version != current_version:
            if upgrade_pypas():
                console.success(
                    f'Upgraded [i]pypas-cli[/i] from [note]{current_version}[/note] to [note]{latest_version}[/note]',
                    emphasis=True,
                )
                console.debug(CHANGELOG_URL.format(version=latest_version.replace('.', '')))
            else:
                console.error('Error upgrading [i]pypas-cli[/i]')
                console.debug(
                    f'Please check [u]{DOCS_UPGRADE_URL}[/u] for manual upgrade instructions'
                )
        else:
            console.success(
                f"You're on the latest version of [i]pypas-cli[/i]: [note]{current_version}[/note]",
            )
    else:
        console.error('Could not determine [i]pypas-cli[/i] version information')
        console.debug(f'Please check [u]{DOCS_UPGRADE_URL}[/u] for manual upgrade instructions')
