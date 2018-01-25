#!/usr/bin/env python

from distutils.core import setup

setup(name='rwimodeling',
      version='1.0.1',
      description='Modeling of Remcom Wireless InSite simulations',
      author='LASSE',
      author_email='pedosb@gmail.com',
      url='https://gitlab.lasse.ufpa.br/software/python-machine-learning/rwi-3d-modeling',
      packages=['rwimodeling'],
      requires=['numpy(>=1.14)']
      )