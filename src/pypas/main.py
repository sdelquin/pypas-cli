import typer
from rich.prompt import Confirm

from pypas import Exercise, User, config, console, utils
from pypas.lib.decorators import inside_exercise

app = typer.Typer(
    add_completion=False,
    help='pypas ⚘ Python Practical Assignments',
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def init(
    version: bool = typer.Option(
        False,
        '--version',
        show_default=False,
        help='Show pypas-cli installed version.',
    ),
):
    if version:
        print(utils.get_pypas_version())


@app.command()
def get(exercise_slug: str = typer.Argument(help='Slug of exercise')):
    """Get exercise."""
    if (exercise := Exercise(exercise_slug)).folder_exists():
        console.print(f'Folder {exercise.cwd_folder} already exists!', style='warning')
        console.print(
            '[italic]If continue, files coming from server will [red]OVERWRITE[/red] your existing files'
        )
        if not Confirm.ask('Continue', default=False):
            return
    if exercise.download():
        exercise.unzip()
        console.print(f'Exercise is available at [note]{exercise.cwd_folder}[/note] [success]✔')


@app.command()
@inside_exercise
def doc():
    """Open documentation for exercise."""
    exercise = Exercise.from_config()
    exercise.open_docs()


@app.command()
@inside_exercise
def update(
    force: bool = typer.Option(
        False, '--force', '-f', help='Force update and omit backup of existing files'
    ),
):
    """Update exercise."""
    exercise = Exercise.from_config()
    exercise.download()
    dir = exercise.unzip(to_tmp_dir=True)
    exercise.update(src_dir=dir, backup=not force)


@app.command()
def auth(token: str = typer.Argument(help='Access token')):
    """Authenticate at pypas.es (token must be given by administrator)"""
    if User(token).authenticate():
        config['token'] = token
        config.save()


@app.command()
def upgrade():
    """Upgrade pypas-cli from PyPI."""
    utils.upgrade_pypas()


if __name__ == '__main__':
    app()
