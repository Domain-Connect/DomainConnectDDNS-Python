#!/usr/bin/env python
from setuptools import setup


setup(
    name = 'domain-connect-dyndns',
    version = '0.0.1',
    description = 'Python client library for Dynamic DNS using Domain Connect',
    license = 'MIT',
    classifiers = [
        'Programming Language :: Python :: 3.5',
    ],
    packages = [
        'dyndns',
    ],
    install_requires = [
        'validators >= 0.12.2',
        'requests >= 2.19.1',
        'dnspython >= 1.15.0',
    ],
    dependency_links = [
        'https://github.com/andreeadima/domainconnect_python/tarball/master#egg=domainconnect_python-0.0.3'
    ],
    entry_points = {
        'console_scripts': ['domain-connect-dyndns=dyndns.command_line:main'],
    }
)