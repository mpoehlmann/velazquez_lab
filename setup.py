#!/usr/bin/env python3
"""Setup Velazquez Lab Python modules."""

from setuptools import setup, find_packages
import numpy as np

with open('README.md') as f:
  readme = f.read()

setup(
  name='velazquez_lab',
  version='1.0.0',
  description=('Analysis code for the Velazquez Lab.'),
  long_description=readme,
  author='Michael Poehlmann',
  author_email='poehlmann@ucdavis.edu',
  url='https://github.com/mpoehlmann/velazquez_lab',
  packages=find_packages(exclude=('tutorials','scripts')),
  # packages=['velazquez_lab',
  #           'scintmc.scint',
  #           'scintmc.utils',
  #           'pyproto',
  #           'pyproto.dselec',
  #          ],
  package_dir={
    'velazquez_lab': 'velazquez_lab',
  },
  # scripts=['scripts/create_pol_curves.py',
  #         ],
  zip_safe=False,
)
