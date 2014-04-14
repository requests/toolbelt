# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup

if sys.argv[-1].lower() in ("submit", "publish"):
    os.system("python setup.py bdist_wheel sdist upload")
    sys.exit()


def get_version():
    version = ''
    with open('requests_toolbelt/__init__.py', 'r') as fd:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fd:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    return version

try:
    from requests_toolbelt import __version__
except:
    __version__ = get_version()

if not __version__:
    raise RuntimeError('Cannot find version information')

from requests_toolbelt import (
    __title__,
    __description__,
    __author__,
    __author_email__,
    __url__,
)

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description="\n\n".join([open("README.rst").read(),
                                  open("HISTORY.rst").read()]),
    license=open("LICENSE").read(),
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    packages=['requests_toolbelt'],
    package_data={'': ['LICENSE', 'AUTHORS.rst']},
    include_package_data=True,
    install_requires=['requests>=2.0.1,<=3.0.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
