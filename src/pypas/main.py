import typer
from rich import print
from rich.prompt import Confirm

from pypas import Exercise, console
from pypas.lib.decorators import inside_exercise

app = typer.Typer(
    add_completion=False,
    help='✨ pypas',
    no_args_is_help=True,
)


@app.command()
def get(exercise_slug: str):
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
    if exercise := Exercise.from_config():
        exercise.open_docs()


@app.command()
@inside_exercise
def update():
    print('TODO!')


if __name__ == '__main__':
    app()
