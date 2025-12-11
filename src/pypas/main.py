from pathlib import Path
from typing import List

import typer
from rich.prompt import Confirm

from pypas import Config, Exercise, User, console, sysutils
from pypas.lib.decorators import auth_required, check_version, inside_exercise

app = typer.Typer(
    add_completion=False,
    help='pypas ⚘ Python Practical Assignments',
    pretty_exceptions_enable=False,
)


# https://peq.es/8ff0b0
@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        '--version',
        show_default=False,
        help='Show pypas-cli installed version.',
    ),
):
    if version:
        sysutils.handle_package_version()
        sysutils.show_package_info()
    # https://typer.tiangolo.com/tutorial/commands/context/#exclusive-executable-callback
    elif ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
@check_version
def get(exercise_slug: str = typer.Argument(help='Slug of exercise')):
    """Get (download) exercise."""
    if (exercise := Exercise(exercise_slug)).folder_exists():
        console.warning(f'Folder ./{exercise.folder} already exists!')
        console.info(
            '[italic]If continue, files coming from server will [red]OVERWRITE[/red] your existing files'
        )
        if not Confirm.ask('Continue', default=False):
            return
    if Config.local_config_exists():
        console.warning('Current folder seems to be a pypas exercise.')
        console.info(
            '[italic]If continue, files coming from server will [red]MESS[/red] your existing files'
        )
        if not Confirm.ask('Continue', default=False):
            return
    config = Config()
    if exercise.download(config.get('token')):
        exercise.unzip()
        console.info(f'Exercise is available at [note]./{exercise.folder}[/note] [success]✔')


@app.command()
@inside_exercise
@check_version
def doc():
    """Open documentation for exercise."""
    exercise = Exercise.from_config()
    exercise.open_docs()


@app.command()
@inside_exercise
@check_version
def update(
    force: bool = typer.Option(
        False, '--force', '-f', help='Force update and omit backup of existing files'
    ),
):
    """Update exercise."""
    # Backup patterns follow fnmatch syntax: https://docs.python.org/3/library/fnmatch.html
    config = Config()
    if (exercise := Exercise.from_config()).download(config.get('token')):
        dir = exercise.unzip(to_tmp_dir=True)
        exercise.update(src_dir=dir, backup=not force)


@app.command()
@check_version
def auth(token: str = typer.Argument(help='Access token')):
    """Authenticate at pypas.es (token required)."""
    if User(token).authenticate():
        config = Config()
        config.save(token=token)


@app.command()
def upgrade():
    """Upgrade pypas-cli from PyPI."""
    sysutils.handle_upgrade_pypas()


@app.command()
@inside_exercise
@check_version
def zip(verbose: bool = typer.Option(False, '--verbose', '-v', help='Increase verbosity.')):
    """Compress exercise contents."""
    # Excluded patterns follow fnmatch syntax: https://docs.python.org/3/library/fnmatch.html
    exercise = Exercise.from_config()
    zipfile = exercise.zip(verbose=verbose)
    size, str_size = sysutils.get_file_size(zipfile)
    console.info(f'Compressed exercise is available at: [note]{zipfile}[/note] [dim]({str_size})')


@app.command()
@auth_required
@inside_exercise
@check_version
def put():
    """Put (upload) exercise."""
    config = Config()
    if nested_config_path := config.find_nested_config(relative_to_cwd=True):
        console.warning(
            f'Another exercise seems to be nested inside current folder: ./{nested_config_path}'
        )
        console.info('[italic]If continue, upload will [red]BREAK[/red] testing[/italic]')
        if not Confirm.ask('Continue', default=False):
            return
    exercise = Exercise.from_config()
    zipfile = exercise.zip(to_tmp_dir=True)
    exercise.upload(zipfile, config['token'])


@app.command(context_settings={'ignore_unknown_options': True})
@inside_exercise
@check_version
def test(
    args: List[str] = typer.Argument(None, help='Arguments passed to test tool'),
):
    """Test exercise."""
    exercise = Exercise.from_config()
    exercise.test(args or [])


@app.command()
@check_version
def log(
    frame: str = typer.Option('', '--frame', '-f', help='Filter by frame.'),
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Increase verbosity.'),
):
    """Log of uploaded assignments."""
    config = Config()
    Exercise.log(config.get('token'), frame, verbose)


@app.command()
@check_version
def list(
    frame: str = typer.Option('', '--frame', '-f', help='Filter by frame.'),
    primary_topic: str = typer.Option('', '--ptopic', '-p', help='Filter by primary topic.'),
    secondary_topic: str = typer.Option('', '--stopic', '-s', help='Filter by secondary topic.'),
):
    """List exercises. Topic in format <primary>/<secondary>"""
    config = Config()
    Exercise.list(config.get('token'), frame, primary_topic, secondary_topic)


@app.command()
@check_version
def unauth():
    """Unauthenticate from pypas.es (clear token)."""
    config = Config()
    config.save(token='')
    console.success('You have been successfully unauthenticated')


@app.command()
@check_version
def run():
    """Run exercise with given args."""
    exercise = Exercise.from_config()
    exercise.run()


@app.command()
@check_version
def pull(
    item_slug: str = typer.Argument(help='Slug of exercise or frame.'),
):
    """Pull (download) specific assignment or all frame assignments."""
    if (dst_folder := Path(item_slug)).exists():
        console.warning(f'Folder ./{dst_folder} already exists!')
        console.info(
            '[italic]If continue, files coming from server will [red]OVERWRITE[/red] your existing files'
        )
        if not Confirm.ask('Continue', default=False):
            return
    config = Config()
    if file := Exercise.pull(item_slug, config.get('token')):
        folder = sysutils.unzip(file, extract_to=dst_folder)
        console.info(f'Assignment(s) are available at [note]./{folder.name}[/note] [success]✔')


if __name__ == '__main__':
    app()
