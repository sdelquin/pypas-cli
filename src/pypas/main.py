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
    config = Config()
    if exercise.download(config.get('token')):
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
    config = Config()
    if (exercise := Exercise.from_config()).download(config.get('token')):
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
def zip(verbose: bool = typer.Option(False, '--verbose', '-v', help='Increase verbosity.')):
    """Compress exercise contents."""
    exercise = Exercise.from_config()
    zipfile = exercise.zip(verbose=verbose)
    size, str_size = sysutils.get_file_size(zipfile)
    console.info(f'Compressed exercise is available at: [note]{zipfile}[/note] [dim]({str_size})')


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
def log(verbose: bool = typer.Option(False, '--verbose', '-v', help='Increase verbosity.')):
    """Log of uploaded exercises."""
    Exercise.show_log(verbose)


@app.command()
def list(
    primary_topic: str = typer.Option('', '--ptopic', '-p', help='Filter by primary topic.'),
    secondary_topic: str = typer.Option('', '--stopic', '-s', help='Filter by secondary topic.'),
):
    """List exercises. Topic in format <primary>/<secondary>"""
    config = Config()
    Exercise.list(config.get('token'), primary_topic, secondary_topic)


if __name__ == '__main__':
    app()
