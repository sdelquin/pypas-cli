import tempfile
from pathlib import Path
from sys import platform

import requests
from tqdm import tqdm


class OS:
    LINUX = 1
    MACOS = 2
    WINDOWS = 3
    OTHER = 4


def download(url: str, fname: str, save_temp=False, chunk_size=1024) -> Path:
    # https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51
    if save_temp:
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        target_file = tmp_file.name
    else:
        target_file = fname
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(target_file, 'wb') as file, tqdm(
        desc=fname, total=total, unit='iB', unit_scale=True, unit_divisor=1024
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)
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
