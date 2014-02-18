from __future__ import print_function
from setuptools import setup, find_packages
import io
import os

import synnefo_ssh

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='synnefo-ssh',
    version=synnefo_ssh.__version__,
    url='http://github.com/cstavr/synnefo-ssh/',
    license='Apache Software License v2.0',
    author='Christos Stavrakakis',
    install_requires=['kamaki>=0.12.9', 'tabulate'],
    author_email='stavr.chris@gmail.com',
    description='Easy SSH to Synnefo Virtual Servers',
    long_description=long_description,
    packages=['synnefo_ssh'],
    include_package_data=True,
    platforms='any',
    scripts=[
        'synnefo_ssh/synsh',
        'synnefo_ssh/snf-create'
    ]
)
