#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='easy2fa',
      version='0.8',
      description='Easy to use two-factor-auth client for cli',
      author='Greg Lutostanski',
      author_email='greg.luto@gmail.com',
      url='https://github.com/lutostag/easy2fa',
      packages=find_packages(),
      classifiers=['Programming Language :: Python :: 3.5'],
      install_requires=['PyYAML'],
      entry_points={'console_scripts': ['easy2fa = easy2fa:main']}
      )
