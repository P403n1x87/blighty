#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import find_packages, setup, Extension

setup(
    name             = 'blighty',
    version          = '0.1.0',
    description      = 'Desktop Widget Manager. Think of conky, but with Python instead of Lua.',
    long_description = open('README.rst').read(),
    author           = 'Gabriele N. Tornetta',
    author_email     = 'phoenix1987@gmail.com',
    url              = 'https://github.com/pypa/blighty',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages         = find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires = ['pycairo', 'pgi'],
)
