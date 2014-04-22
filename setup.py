#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
distutils script for openmolar1.
see https://docs.python.org/2/distutils/configfile.html for explanation
'''

from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as _sdist
from distutils.core import setup
from distutils.dep_util import newer
from distutils.log import info

import glob
import os
import shutil
import sys

OM_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")
sys.path.insert(0, OM_PATH)

from openmolar.settings import version

VERSION = version.VERSION


class sdist(_sdist):

    '''
    overwrite distutils standard source code builder to remove
    extraneous code from version.py
    '''
    version_filepath = version.__file__
    backup_version_filepath = version_filepath + "_orig"

    def run(self, *args, **kwargs):
        self.tear_down()
        _sdist.run(self, *args, **kwargs)
        self.clean_up()

    def tear_down(self):
        print "rewriting version"
        f = open(self.version_filepath, "r")
        new_data = ""
        add_line = True
        for line in f:
            print line
            if line.startswith("VERSION ="):
                print "MATCH"
                new_data += "VERSION = %s\n\n\n" % VERSION
                add_line = False
            elif line.startswith("if __name__"):
                add_line = True
            if add_line:
                new_data += line

        shutil.move(self.version_filepath, self.backup_version_filepath)
        f = open(self.version_filepath, "w")
        f.write(new_data)
        f.close()

    def clean_up(self):
        os.remove(self.version_filepath)
        shutil.move(self.backup_version_filepath, self.version_filepath)


class InstallData(install_data):

    '''
    re-implement class distutils.install_data install_data
    compile binary translation files for gettext
    '''

    def run(self):
        print "COMPILING PO FILES"
        i18nfiles = []
        if not os.path.isdir("src/openmolar/locale/"):
            print "WARNING - language files are missing!"
        for po_file in glob.glob("src/openmolar/locale/*.po"):
            directory, file_ = os.path.split(po_file)
            lang = file_.replace(".po", "")
            mo_dir = os.path.join(directory, lang)
            try:
                os.mkdir(mo_dir)
            except OSError:
                pass
            mo_file = os.path.join(mo_dir, "openmolar.mo")
            if not os.path.exists(mo_file) or newer(po_file, mo_file):
                cmd = 'msgfmt -o %s %s' % (mo_file, po_file)
                info('compiling %s -> %s' % (po_file, mo_file))
                if os.system(cmd) != 0:
                    info('Error while running msgfmt on %s' % po_file)

            destdir = os.path.join("/usr", "share", "locale", lang,
                                   "LC_MESSAGES")

            i18nfiles.append((destdir, [mo_file]))

        self.data_files.extend(i18nfiles)
        install_data.run(self)


setup(
    name='openmolar',
    version=VERSION,
    description='Open Source Dental Practice Management Software',
    author='Neil Wallace',
    author_email='neil@openmolar.com',
    url='https://www.openmolar.com',
    license='GPL v3',
    package_dir={'openmolar': 'src/openmolar'},
    packages=['openmolar',
                'openmolar.backports',
                'openmolar.dbtools',
                'openmolar.schema_upgrades',
                'openmolar.qt4gui',
                'openmolar.qt4gui.dialogs',
                'openmolar.qt4gui.appointment_gui_modules',
                'openmolar.qt4gui.charts',
                'openmolar.qt4gui.compiled_uis',
                'openmolar.qt4gui.customwidgets',
                'openmolar.qt4gui.dialogs',
                'openmolar.qt4gui.fees',
                'openmolar.qt4gui.feescale_editor',
                'openmolar.qt4gui.phrasebook',
                'openmolar.qt4gui.printing',
                'openmolar.qt4gui.printing.gp17',
                'openmolar.qt4gui.tools',
                'openmolar.settings',
                'openmolar.ptModules'],
    package_data={'openmolar': ['resources/icons/*.*',
                                'resources/teeth/*.png',
                                'resources/gp17/*.jpg',
                                'resources/gp17-1/*.png',
                                'resources/feescales/*.xml',
                                'resources/feescales/*.xsd',
                                'resources/phrasebook/*.*',
                                'resources/*.*',
                                'html/*.*',
                                'html/images/*.*',
                                'html/firstrun/*.*', ]},
    data_files=[
        ('/usr/share/man/man1', ['bin/openmolar.1']),
        ('/usr/share/icons/hicolor/scalable/apps', ['bin/openmolar.svg']),
        ('/usr/share/applications', ['bin/openmolar.desktop']), ],
    cmdclass={'sdist': sdist,
              'install_data': InstallData},
    scripts=['openmolar'],
)
