#!/usr/bin/env python

from distutils.core import setup
import glob

setup(name='openMolar',
      version='0.0.6',
      description='open Source dental practice management software',
      author='Neil Wallace',
      author_email='rowinggolfer@googlemail.com',
      url='https://launchpad.net/openmolar',
      license='GPL v3',
      data_files = [ ('openmolar', ['demoDataBase.sql']),
                     ('openmolar/resources', glob.glob('resources/*')),
                     ('openmolar/qt-designer', glob.glob('qt-designer/*.ui')) ],
      scripts=['openmolar'],
      package_dir = { 'openmolar': '',
                      'openmolar.dbtools': 'dbtools',
                      'openmolar.ptModules': 'ptModules',
                      'openmolar.qt4gui': 'qt4gui',
                      'openmolar.qt-designer': 'qt-designer',
                      'openmolar.resources': 'resources',
                      'openmolar.settings': 'settings' },
      packages=['openmolar',
      'openmolar.dbtools',
      'openmolar.ptModules',
      'openmolar.qt4gui',
      'openmolar.qt-designer',
      'openmolar.resources',
      'openmolar.settings'],
     )

