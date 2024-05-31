import functools
import re

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table
from rich.theme import Theme

STYLES = {
    'info': '',
    'error': 'bold red',
    'success': 'bold green',
    'warning': 'yellow',
    'quote': 'cyan',
    'note': ' bold blue',
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

    def message(self, msg: str, style: str, *args, emphasis=False, cr=True, **kwargs):
        if not isinstance(msg, str):
            msg = str(msg)
        if emphasis and not re.search(r'https?://\S+$', msg):
            msg += '!'
        end = '\n' if cr else ' '
        self.print(msg, *args, style=style, end=end, **kwargs)

    info = functools.partialmethod(message, style='info')
    warning = functools.partialmethod(message, style='warning')
    error = functools.partialmethod(message, style='error', emphasis=True)
    success = functools.partialmethod(message, style='success', emphasis=True)
    note = functools.partialmethod(message, style='note')
    highlight = functools.partialmethod(message, style='highlight')
    debug = functools.partialmethod(message, style='dim')


class CustomTable(Table):
    def __init__(self, *columns):
        super().__init__()
        for name, style in columns:
            self.add_column(name, style=style)


console = CustomConsole(theme=custom_theme, highlight=False)
