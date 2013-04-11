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


from printemps import __version__


setup(
    name='Printemps',
    version=__version__,
    url='https://github.com/Printemps/Printemps',
    license='AGPL',
    author='Amirouche Boubekki',
    author_email='amirouche.boubekki@gmail.com',
    description='Python graph database lovestory',
    long_description=__doc__,
    py_modules=['printemps'],
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
            'printemps = printemps:main',
        ]
    }

)
