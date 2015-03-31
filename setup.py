# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the GNU General Public License, Version 2.0

import os

from setuptools import find_packages
from setuptools import setup


setup(
    name='launchpad_client',
    version='0.1',
    description='High-level Library for manipulating bugs on Launchpad',
    author='Mirantis, Inc.',
    author_email='fuel-osci@mirantis.com',
    url='http://mirantis.com',
    keywords='launchpad bug mirantis',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    py_modules=['launchpad_client'],
    install_requires=[_.strip() for _ in open('requirements.txt').readlines()]
)
