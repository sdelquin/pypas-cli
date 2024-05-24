import os
import zipfile
from urllib.parse import urljoin

import typer
from rich import print

from pypas import settings
from pypas.lib import utils
from pypas.lib.console import console

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
    console.print(f'Getting exercise from: {exercise_url}')
    fname = utils.download(exercise_url, f'{exercise_slug}.zip', save_temp=True)
    console.print('Inflating exercise bundle', end=' ')
    with zipfile.ZipFile(fname) as zip_ref:
        zip_ref.extractall()
    console.print('✔', style='success')
    os.remove(fname)
    console.print(
        f'Exercise is available at folder [info]./{exercise_slug}[/info] [success]✔[/success]'
    )


@app.command()
def doc():
    if not os.path.exists('docs'):
        console.print(
            '[bold red][🞫 Error][/bold red] Current folder doesn\'t have a "docs" folder!'
        )
    else:
        os.system(f'{utils.get_open_cmd()} docs/README.pdf')


if __name__ == '__main__':
    app()
