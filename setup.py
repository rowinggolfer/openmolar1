#!/usr/bin/env python

from distutils.core import setup
import glob

from distutils.core import setup, Extension
from distutils.command.install_data import install_data

# Pete Shinner's distutils data file fix... from distutils-sig
#  data installer with improved intelligence over distutils
#  data files are copied into the project directory instead
#  of willy-nilly
class smart_install_data(install_data):   
    def run(self):
        # need to change self.install_dir to the library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)



setup(name='openmolar',
      version='0.0.6',
      description='open Source dental practice management software',
      author='Neil Wallace',
      author_email='rowinggolfer@googlemail.com',
      url='https://launchpad.net/openmolar',
      license='GPL v3',
      cmdclass = { 'install_data': smart_install_data },
      data_files = [ ('openmolar', ['demoDataBase.sql']),
                     #('openmolar/resources', glob.glob('resources/*')),
                     ('openmolar/resources/icons', glob.glob('resources/icons/*')),
                     ('openmolar/qt-designer', glob.glob('qt-designer/*.ui')) ],
      scripts=['openmolar'],
      package_dir = { 'openmolar': '',
                      'openmolar.dbtools': 'dbtools',
                      'openmolar.ptModules': 'ptModules',
                      'openmolar.qt4gui': 'qt4gui',
                      'openmolar.qt4gui.dialogs': 'qt4gui/dialogs',
                      'openmolar.qt4gui.customwidgets': 'qt4gui/customwidgets',
                      'openmolar.qt4gui.printing': 'qt4gui/printing',
                      #'openmolar.qt-designer': 'qt-designer',
                      #'openmolar.resources': 'resources',
                      'openmolar.settings': 'settings' },
      packages=['openmolar',
      'openmolar.dbtools',
      'openmolar.ptModules',
      'openmolar.qt4gui',
      'openmolar.qt4gui.dialogs',
      'openmolar.qt4gui.customwidgets',
      'openmolar.qt4gui.printing',
      'openmolar.qt-designer',
      'openmolar.resources',
      'openmolar.settings'],
     )

