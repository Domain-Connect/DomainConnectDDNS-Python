#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'domain-connect-dyndns',
    version = '0.0.5',
    description = 'Python client library for Dynamic DNS using Domain Connect',
    license = 'MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Andreea Dima',
    author_email = 'andreea.dima@1and1.ro',
    url="https://github.com/Domain-Connect/DomainConnectDDNS-Python",
    classifiers = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    packages = [
        'dyndns',
    ],
    install_requires = [
        'validators >= 0.12.2',
        'requests >= 2.19.1',
        'dnspython >= 1.15.0',
        'domain-connect >= 0.0.7',
    ],
    entry_points = {
        'console_scripts': ['domain-connect-dyndns=dyndns.command_line:main'],
    }
)