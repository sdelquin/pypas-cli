import typer

app = typer.Typer(
    add_completion=False,
    help='✨ pypas',
    no_args_is_help=True,
)


@app.command()
def run():
    print('Hi there!')


if __name__ == '__main__':
    app()
