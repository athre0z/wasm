#!/usr/bin/env python
#  -*- coding: utf8 -*-

from setuptools import setup

setup(
    name='wasm',
    version='1.0b0',
    packages=['wasm'],
    url='https://github.com/athre0z/wasm',
    license='MIT',
    author='Joel Höner',
    author_email='athre0z@zyantific.com',
    description='WebAssembly decoder',
    install_requires=[
        'setuptools',
    ],
    entry_points={
        'console_scripts': [
            'wasmdump = wasm.__main__:dump'
        ]
    }
)
