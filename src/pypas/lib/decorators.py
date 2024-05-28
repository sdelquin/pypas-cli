import functools
import os

from .console import console


def inside_exercise(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not os.path.exists('.pypas.toml'):
            console.print('Current folder does not seem to be a pypas exercise!', style='danger')
        else:
            return func(*args, **kwargs)

    return wrapper
