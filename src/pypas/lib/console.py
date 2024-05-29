from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        'info': 'cyan',
        'warning': 'yellow',
        'danger': 'bold red',
        'success': 'bold green',
        'note': 'bold blue',
        'highlight': 'bold purple',
    }
)


class CustomConsole(Console):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def done(self, msg: str = ''):
        if msg:
            msg = f'{msg} '
        self.print(f'{msg}[bold green]✔')

    def great(self, msg: str = ''):
        if msg:
            msg = f'{msg} '
        self.print(f'{msg}[yellow bold]✶')


console = CustomConsole(theme=custom_theme, highlight=False)
