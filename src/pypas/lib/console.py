from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        'info': 'cyan',
        'warning': 'yellow',
        'danger': 'bold red',
        'success': 'bold green',
    }
)

console = Console(theme=custom_theme)
