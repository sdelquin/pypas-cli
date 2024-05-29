import typer
from rich.prompt import Confirm

from pypas import Exercise, console
from pypas.lib.decorators import inside_exercise

app = typer.Typer(
    add_completion=False,
    help='✨ pypas → Python Practical Assignments',
    no_args_is_help=True,
)


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


if __name__ == '__main__':
    app()
