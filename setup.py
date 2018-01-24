#!/usr/bin/env python

from distutils.core import setup

setup(name='rwimodeling',
      version='1.0',
      description='Parsing of Remcom Wireless InSite .p2m files',
      author='LASSE',
      author_email='pedosb@gmail.com',
      url='https://gitlab.lasse.ufpa.br/software/python-machine-learning/rwi-parsing',
      packages=['rwimodeling'],
      requires=['numpy(>=1.14)']
      )