#!/usr/bin/env python

from os.path import join

from setuptools import setup, find_packages


NAME = 'django-softdeletion'
PACKAGE = NAME.replace('-', '_')
CLASSIFIERS = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
Framework :: Django
Programming Language :: Python :: 2.7
"""
REQUIREMENTS = open('requirements/base.txt').read()


def get_version():
    with open(join(PACKAGE, '__init__.py')) as fileobj:
        for line in fileobj:
            if line.startswith('__version__ ='):
                return line.split('=', 1)[1].strip()[1:-1]
        else:
            raise Exception(
                '__version__ is not defined in %s.__init__' % PACKAGE)


setup(
    name=NAME,
    version=get_version(),
    description='Soft deletion mixin for Django models',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='runtests.runtests',
)
