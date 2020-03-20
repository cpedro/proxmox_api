#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import pve

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

with io.open(os.path.join(here, 'LICENSE'), encoding='utf-8') as f:
    license = '\n' + f.read()

required = []
with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    for line in f.readlines():
        if not line.startswith('#'):
            required.append(line)

setup(
    name='pve',
    version=pve.__version__,
    description='Admin Proxmox VE via Python through web API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Chris Pedro',
    author_email='chris@thepedros.com',
    url='https://github.com/cpedro/proxmox_api',
    python_requires='>=3.6.0',
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=required,
    include_package_data=True,
    license=license,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)

