#!/usr/bin/env python

from distutils.core import setup

setup(name='rwimodeling',
      version='1.0.3',
      description='Modeling of Remcom Wireless InSite simulations',
      author='LASSE',
      author_email='pedosb@gmail.com',
      url='https://github.com/lasseufpa/5gm-rwi-3d-modeling',
      packages=['rwimodeling'],
      requires=['numpy(>=1.14)']
      )