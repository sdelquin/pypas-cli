# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

REQUIREMENTS = ()

setup(
    name='pypas-cli',
    version='0.0.1',
    url='https://github.com/sdelquin/pypas.git',
    author='Sergio Delgado Quintero',
    author_email='sdelquin@gmail.com',
    description='pypas',
    license='MIT',
    packages=['pypas'],
    install_requires=REQUIREMENTS,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
