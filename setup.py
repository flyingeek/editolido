# coding=utf-8
from distutils.core import setup
import re

with open('editolido/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='editolido',
    version=version,
    packages=['editolido'],
    package_data={'editolido': ['data/*.*', 'data/.wmogrid.json']},
    url='https://github.com/flyingeek/editolido',
    download_url='https://github.com/flyingeek/editolido/archive/master.zip',
    license='',
    author='Eric Delord',
    author_email='',
    description='Utilities for playing with Lido and Editorial IOS app'
)
