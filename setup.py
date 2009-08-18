#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'openmolar',
    version = '0.1.2',
    description = 'Open Source Dental Practice Management Software',
    author = 'Neil Wallace',
    author_email = 'rowinggolfer@googlemail.com',
    url = 'https://launchpad.net/openmolar',
    license = 'GPL v3',
    package_dir = {'openmolar' : 'src/openmolar'},
    packages = ['openmolar',
                'openmolar.dbtools',
                'openmolar.qt4gui',
                'openmolar.qt4gui.dialogs',
                'openmolar.qt4gui.appointment_gui_modules',
                'openmolar.qt4gui.customwidgets',
                'openmolar.qt4gui.dialogs',
                'openmolar.qt4gui.fees',
                'openmolar.qt4gui.printing',
                'openmolar.qt4gui.tools',
                'openmolar.settings',
                'openmolar.ptModules'],
    package_data = {'openmolar' : ['resources/icons/*.*',
                                    'resources/*.*',
                                    'html/*.*',
                                    'html/images/*.*',
                                    'html/firstrun/*.*'] },
    data_files=[('share/icons/hicolor/scalable/apps', ['bin/openmolar.svg']),
                ('share/applications', ['bin/openmolar.desktop'])],
    scripts = ['openmolar'],
    )

