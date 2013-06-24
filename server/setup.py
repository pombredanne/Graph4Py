#!/usr/bin/env python
import os

from setuptools import setup


def long_description():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'README.rst')
    try:
        with open(path) as f:
            return f.read()
    except:
        return ''


__doc__ = long_description()


setup(
    name='graph4py',
    version='0.2',
    url='https://github.com/python-graph-lovestory/Graph4Py',
    license='AGPL',
    author='Amirouche Boubekki',
    author_email='amirouche.boubekki@gmail.com',
    description='Python graph database lovestory',
    long_description=__doc__,
    py_modules=['graph4py'],
    zip_safe=False,
    platforms='any',
    install_requires=['setproctitle', 'blueprints'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'graph4py = graph4py:main',
        ]
    }
)
