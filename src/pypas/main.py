import typer
from rich.prompt import Confirm

from pypas import Config, Exercise, User, console, sysutils
from pypas.lib.decorators import auth_required, inside_exercise

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
        print(sysutils.get_pypas_version())


@app.command()
def get(exercise_slug: str = typer.Argument(help='Slug of exercise')):
    """Get (download) exercise."""
    if (exercise := Exercise(exercise_slug)).folder_exists():
        console.warning(f'Folder ./{exercise.folder} already exists!')
        console.info(
            '[italic]If continue, files coming from server will [red]OVERWRITE[/red] your existing files'
        )
        if not Confirm.ask('Continue', default=False):
            return
    if exercise.download():
        exercise.unzip()
        console.info(f'Exercise is available at [note]./{exercise.folder}[/note] [success]✔')


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
    if (exercise := Exercise.from_config()).download():
        dir = exercise.unzip(to_tmp_dir=True)
        exercise.update(src_dir=dir, backup=not force)


@app.command()
def auth(token: str = typer.Argument(help='Access token')):
    """Authenticate at pypas.es (token required)."""
    if User(token).authenticate():
        config = Config()
        config.save(token=token)


@app.command()
def upgrade():
    """Upgrade pypas-cli from PyPI."""
    sysutils.upgrade_pypas()


@app.command()
@inside_exercise
def zip(
    verbose: bool = typer.Option(False, '--list', '-l', help='List compressed files.'),
):
    """Compress exercise contents."""
    exercise = Exercise.from_config()
    zipfile = exercise.zip(verbose=verbose)
    zipfile_size = sysutils.get_file_size(zipfile)
    console.info(
        f'Compressed exercise is available at: [note]{zipfile}[/note] [dim]({zipfile_size} kB)'
    )


@app.command()
@auth_required
@inside_exercise
def put():
    """Put (upload) exercise."""
    exercise = Exercise.from_config()
    zipfile = exercise.zip(to_tmp_dir=True)
    config = Config()
    exercise.upload(zipfile, config['token'])


@app.command()
@inside_exercise
def test(
    help: bool = typer.Option(False, '--help', '-h', help='Show test options.'),
):
    """Test exercise."""
    exercise = Exercise.from_config()
    if help:
        exercise.pytest_help()
    else:
        exercise.test()


@app.command()
@inside_exercise
def stats():
    """Get stats of uploaded exercises."""
    exercise = Exercise.from_config()
    exercise.show_stats()


if __name__ == '__main__':
    app()
