#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'dnstest',
    'version': '0.1',
    'description': 'DNSSEC-trigger testing suite',
    'author': 'Martin Sehnoutka',
    'url': 'https://github.com/msehnout/dnssec-trigger-testing',
    'author_email': 'msehnout@redhat.com',
    'install_requires': ['nose'],
    'packages': ['dnstest'],
    'scripts': ['bin/dnssec-testing-setup'],
    'package_data' : {'': ['templates/*']},
}

setup(**config)
