#!/usr/bin/env python
from setuptools import setup
import dyndns

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = [
    'unittest2 >= 1.1.0',
]

setup(
    name = 'domain-connect-dyndns',
    version=dyndns.__version__,
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
        'validators >= 0.12.6',
        'requests >= 2.21.0',
        'dnspython >= 1.15.0',
        'domain-connect >= 0.0.9',
        'ipaddress >= 1.0.23;python_version<"3.3"',
    ],
    entry_points = {
        'console_scripts': ['domain-connect-dyndns=dyndns.command_line:main'],
    },
    tests_require=test_deps,
    extras_require={
        'test': test_deps,
    },
)
