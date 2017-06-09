#!/usr/bin/env python
#  -*- coding: utf8 -*-

from setuptools import setup

setup(
    name='wasm',
    version='1.1',
    packages=['wasm'],
    url='https://github.com/athre0z/wasm',
    download_url='https://github.com/athre0z/wasm/archive/v0.1.tar.gz',
    keywords=['wasm', 'disassembler', 'decoder'],
    license='MIT',
    author='Joel Höner',
    author_email='athre0z@zyantific.com',
    description='WebAssembly decoder & disassembler',
    install_requires=[
        'setuptools',
    ],
    entry_points={
        'console_scripts': [
            'wasmdump = wasm.__main__:dump'
        ]
    }
)
