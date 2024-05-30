import functools

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.theme import Theme

STYLES = {
    'info': 'cyan',
    'warning': 'yellow',
    'note': ' bold blue',
    'error': 'bold red',
    'success': 'bold green',
    'highlight': 'bold yellow',
}

PROGRESS_ITEMS = (
    TextColumn('[bold blue]{task.fields[filename]}'),
    BarColumn(),
    '[progress.percentage]{task.percentage:>3.1f}%',
    '•',
    DownloadColumn(),
    '•',
    TransferSpeedColumn(),
    '•',
    TimeRemainingColumn(),
)

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

    def message(self, msg: str, style: str, *args, emphasis=False, **kwargs):
        if not isinstance(msg, str):
            msg = str(msg)
        if emphasis:
            msg += '!'
        self.print(msg, *args, style=style, **kwargs)

    info = functools.partialmethod(message, style='info')
    warning = functools.partialmethod(message, style='warning')
    error = functools.partialmethod(message, style='error', emphasis=True)
    success = functools.partialmethod(message, style='success', emphasis=True)
    note = functools.partialmethod(message, style='note')
    highlight = functools.partialmethod(message, style='highlight')
    debug = functools.partialmethod(message, style='dim')


console = CustomConsole(theme=custom_theme, highlight=False)
