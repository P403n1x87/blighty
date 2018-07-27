#!/usr/bin/env python

"""
This file is part of "blighty" which is released under GPL.

See file LICENCE or go to http://www.gnu.org/licenses/ for full license
details.

blighty is a desktop widget creation and management library for Python 3.

Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import Extension, find_packages, setup

x11 = Extension('blighty._x11',
    include_dirs       = ['/usr/include/cairo/'],
    libraries          = ['cairo', 'X11'],
    extra_compile_args = ['-std=c99'],
    sources            = [
        'blighty/x11/_x11module.c',
        'blighty/x11/atelier.c',
        'blighty/x11/base_canvas.c',
    ]
)


setup(
    name             = 'blighty',
    version          = '2.1.2',
    description      = 'Desktop Widget Manager. Think of conky, but with Python instead of Lua.',
    long_description = open('README.md').read(), long_description_content_type='text/markdown',
    author           = 'Gabriele N. Tornetta',
    author_email     = 'phoenix1987@gmail.com',
    url              = 'https://github.com/P403n1x87/blighty',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords         = 'desklet widget infotainment',
    packages         = find_packages(exclude=['contrib', 'docs', 'tests']),
    ext_modules      = [x11],
    install_requires = ['pycairo'],
    extras_require   = {
        'test': ['pytest-xvfb', 'numpy', 'matplotlib', 'psutil'],
    },
    project_urls     = {
        'Bug Reports' : 'https://github.com/P403n1x87/blighty/issues',
        'Source'      : 'https://github.com/P403n1x87/blighty',
    },
)
