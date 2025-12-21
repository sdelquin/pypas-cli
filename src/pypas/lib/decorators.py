import functools
import os

from pypas import sysutils

from .config import Config
from .console import console
from .exercise import Exercise


def inside_exercise(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if os.path.exists('.pypas.toml'):
            return func(*args, **kwargs)
        else:
            console.error('Current folder does not seem to be a pypas exercise', emphasis=True)
            console.info('Please [note]cd[/note] into the right folder.')

    return wrapper


def auth_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = Config()
        if config.get('token'):
            return func(*args, **kwargs)
        else:
            console.error('You must be authenticated before uploading any exercise', emphasis=True)
            console.info('Run [note]pypas auth --help[/note] for more information.')

    return wrapper


def check_pypas_version(_func=None, *, confirm=False, confirm_suffix: str = ''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if sysutils.handle_package_version(confirm=confirm, confirm_suffix=confirm_suffix):
                return func(*args, **kwargs)

        return wrapper

    return decorator(_func) if _func else decorator


def check_exercise_version(_func=None, *, confirm=False, confirm_suffix: str = ''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            exercise = Exercise.from_config()
            if exercise.handle_exercise_version(confirm=confirm, confirm_suffix=confirm_suffix):
                return func(*args, **kwargs)

        return wrapper

    return decorator(_func) if _func else decorator
