#!/usr/bin/env python

from setuptools import find_packages, setup, Extension


x11 = Extension('blighty.x11',
    include_dirs = ['/usr/include/cairo/'],
    libraries    = ['cairo', 'X11'],
    sources      = [
        'blighty/x11/x11module.c',
        'blighty/x11/canvas.c',
        'blighty/x11/atelier.c',
    ]
)


setup(
    name             = 'blighty',
    version          = '0.1.0',
    description      = 'Desktop Widget Manager. Think of conky, but with Python instead of Lua.',
    long_description = open('README.md').read(),
    author           = 'Gabriele N. Tornetta',
    author_email     = 'phoenix1987@gmail.com',
    url              = 'https://github.com/pypa/blighty',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

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
        'test': ['numpy', 'matplotlib', 'psutil'],
    },
    project_urls     = {
        'Bug Reports' : 'https://github.com/pypa/blighty/issues',
        'Source'      : 'https://github.com/pypa/blighty/',
    },
)
