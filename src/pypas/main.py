import os
import tempfile
import zipfile
from urllib.parse import urljoin

import requests
import typer
from pypas import settings

app = typer.Typer(
    add_completion=False,
    help='✨ pypas',
    no_args_is_help=True,
)


@app.command()
def run():
    print('Hi there!')


@app.command()
def get(exercise_slug: str):
    exercise_url = urljoin(settings.PYPAS_EXERCISES_URLPATH, exercise_slug + '/')
    print(exercise_url)
    response = requests.get(exercise_url)
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
    with zipfile.ZipFile(tmp_file.name) as zip_ref:
        zip_ref.extractall()
    os.remove(tmp_file.name)


if __name__ == '__main__':
    app()
