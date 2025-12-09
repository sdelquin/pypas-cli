import functools
import os

from pypas import sysutils

from .config import Config
from .console import console


def inside_exercise(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if os.path.exists('.pypas.toml'):
            return func(*args, **kwargs)
        else:
            console.error('Current folder does not seem to be a pypas exercise')
            console.info('Please [note]cd[/note] into the right folder.')

    return wrapper


def auth_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = Config()
        if config.has_token():
            return func(*args, **kwargs)
        else:
            console.error('You must be authenticated before uploading any exercise')
            console.info('Run [note]pypas auth --help[/note] for more information.')

    return wrapper


def check_version(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sysutils.handle_package_version()
        return func(*args, **kwargs)

    return wrapper
