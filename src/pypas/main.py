import typer
from rich.prompt import Confirm

from pypas import Config, Exercise, User, console, utils
from pypas.lib.decorators import inside_exercise

app = typer.Typer(
    add_completion=False,
    help='pypas ⚘ Python Practical Assignments',
    no_args_is_help=True,
    pretty_exceptions_enable=False,
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
    else:
        console.print(f'Check the exercise slug: [note]{exercise_slug}')
        console.print('Otherwise contact the administrator.')


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
    """Authenticate at pypas.es (token required)."""
    if User(token).authenticate():
        config = Config()
        config['token'] = token
        config.save()


@app.command()
def upgrade():
    """Upgrade pypas-cli from PyPI."""
    utils.upgrade_pypas()


@app.command()
@inside_exercise
def zip(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Increase output verbose'),
):
    """Compress exercise contents."""
    exercise = Exercise.from_config()
    exercise.zip(verbose=verbose)


if __name__ == '__main__':
    app()
