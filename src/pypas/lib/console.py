import functools

from rich.console import Console
from rich.theme import Theme

STYLES = {
    'info': 'bold cyan',
    'warning': 'bold yellow',
    'error': 'bold red',
    'success': 'bold green',
    'note': 'bold blue',
    'highlight': 'bold yellow',
}

custom_theme = Theme(STYLES)


class CustomConsole(Console):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check(self, msg: str = ''):
        if msg:
            msg = f'{msg} '
        self.print(f'{msg}[success]✔')

    def fail(self, msg: str = ''):
        if msg:
            msg = f'{msg} '
        self.print(f'{msg}[error]✘')

    def splash(self, msg: str = ''):
        if msg:
            msg = f'{msg} '
        self.print(f'{msg}[great]✶')

    def message(self, msg: str, style: str):
        self.print(msg, style=style)


for style in STYLES:
    setattr(CustomConsole, style, functools.partialmethod(CustomConsole.message, style=style))


console = CustomConsole(theme=custom_theme, highlight=False)
