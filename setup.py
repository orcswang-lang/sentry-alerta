#!/usr/bin/env python
"""
sentry-alerta
==============

An extension for Sentry which integrates with Alerta. It will forwards
notifications to an alerta.
"""
from setuptools import setup, find_packages

install_requires = [
    'sentry>=6.0.0',
]

setup(
    name='sentry-alerta',
    version='0.1.0',
    author='OrcsWang',
    author_email='wangxiaoguo@changingedu.com',
    url='https://github.com/jay1412008/sentry-alerta',
    description='A Sentry extension which integrates with Alerta.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'sentry_alerta = sentry_alerta',
        ],
        'sentry.plugins': [
            'alerta = sentry_alerta.models:AlertaMessage',
         ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
