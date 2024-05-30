import tempfile
from pathlib import Path

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from rich.progress import (
    Progress,
)

from .console import PROGRESS_ITEMS, console


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
        console.error(err, emphasis=False)
        return None
    with open(target_file, 'wb') as file, Progress(*PROGRESS_ITEMS) as progress:
        total = int(resp.headers.get('content-length', 0))
        task_id = progress.add_task('download', filename=filename, total=total)
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            progress.update(task_id, advance=size)
    return Path(target_file)


def upload(url: str, fields: dict, filepath: Path, filename: str = '') -> tuple[bool, str]:
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
        response = requests.post(url, data=m, headers=headers, stream=True)

    try:
        response.raise_for_status()
    except Exception as err:
        return False, str(err)
    else:
        data = response.json()
        return data['success'], data['payload']
