#!/usr/bin/env python3

from setuptools import setup

setup(name='netwatch',
      version='0.1',
      description='Watch things on the Internet',
      author='Ben de Graaff',
      author_email='ben@awoo.nl',
      url='https://awoo.nl/netwatch/',
      install_requires=[
          'PyYAML',
          'feedparser',
          'bs4',
          'requests',
          'twitter',
      ],
      packages=['netwatch'],
      scripts=['bin/netwatch'])
