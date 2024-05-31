import tempfile
from pathlib import Path

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from rich.progress import (
    Progress,
)

from .console import PROGRESS_ITEMS
from .monads import Monad


def download(url: str, filename: str, save_temp=False, chunk_size=1024) -> Monad:
    # https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51
    target_file = tempfile.mkstemp(suffix='.zip')[1] if save_temp else filename
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except Exception as err:
        return Monad(Monad.ERROR, err)
    if response.headers.get('content-type') == 'application/json':
        if not (data := response.json())['success']:
            return Monad(Monad.ERROR, data['payload'])
    with open(target_file, 'wb') as file, Progress(*PROGRESS_ITEMS) as progress:
        filesize = int(response.headers.get('content-length', 0))
        task_id = progress.add_task('download', filename=filename, total=filesize)
        for data in response.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            progress.update(task_id, advance=size)
    return Monad(Monad.SUCCESS, Path(target_file))


def upload(url: str, fields: dict, filepath: Path, filename: str = '') -> Monad:
    # https://stackoverflow.com/a/67726532
    def update_progress(monitor):
        pending = filesize - task.completed
        delta = monitor.bytes_read - task.completed
        progress.update(task_id, advance=min(pending, delta))

    filename = filename or filepath.name
    with open(filepath, 'rb') as file, Progress(*PROGRESS_ITEMS) as progress:
        filesize = filepath.stat().st_size
        task_id = progress.add_task('upload', filename=filename, total=filesize)
        task = progress.tasks[0]
        fields['file'] = (filename, file)
        e = MultipartEncoder(fields=fields)
        m = MultipartEncoderMonitor(e, update_progress)
        headers = {'Content-Type': m.content_type}
        try:
            response = requests.post(url, data=m, headers=headers, stream=True)
        except Exception as err:
            return Monad(Monad.ERROR, err)

    try:
        response.raise_for_status()
    except Exception as err:
        return Monad(Monad.ERROR, err)
    else:
        data = response.json()
        return Monad(data['success'], data['payload'])
