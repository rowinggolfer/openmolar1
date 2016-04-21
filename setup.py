#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
distutils script for openmolar1.
see https://docs.python.org/2/distutils/configfile.html for explanation
'''

from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as _sdist
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.core import setup
from distutils.core import Command
from distutils.dep_util import newer
from distutils.log import info

import glob
import os
import re
import shutil
import subprocess
import sys
import unittest
import platform

from PyQt5 import uic
from PyQt5.Qt import PYQT_VERSION_STR

OM_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")
sys.path.insert(0, OM_PATH)

from openmolar.settings import version

VERSION = version.VERSION
RESOURCE_FILE = os.path.join(OM_PATH, "openmolar", "qt4gui", "resources_rc.py")
IS_WINDOWS = platform.system() == 'Windows'
USR = ""
if not IS_WINDOWS:
    USR = "/usr/"


def version_fixes(pydata):
    '''
    apply some specific fixes to the compiled ui files.
    '''
    if PYQT_VERSION_STR < "5.3.2":
        pydata = pydata.replace(
            "MainWindow.setUnifiedTitleAndToolBarOnMac(False)",
            "# MainWindow.setUnifiedTitleAndToolBarOnMac(False)"
        )

    return pydata


class MakeUis(Command):
    '''
    compile qt-designer files and qresources.
    these files vary as the uic module advances, meaning files created on
    debian testing may not work on debian stable etc...
    '''

    description = 'compile ui files and resources into python files'
    user_options = []
    REMOVALS = ("        _translate = QtCore.QCoreApplication.translate\n",)

    REPLACEMENTS = [("import resources_rc",
                     "from openmolar.qt4gui import resources_rc")]

    SRC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "src", "openmolar", "qt-designer")

    DEST_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "src", "openmolar", "qt4gui", "compiled_uis")



    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def gettext_wrap(self, match):
        '''
        a callable used form regex substitution
        '''
        return '_(%s)' % match.groups()[1].strip(" ")

    def de_bracket(self, match):
        '''
        a callable used form regex substitution
        '''
        return match.groups()[0].strip("()")

    def compile_ui(self, ui_fname, outdir):
        name = os.path.basename(ui_fname)
        outname = "Ui_%s.py" % name.rstrip(".ui")
        pyfile = os.path.join(outdir, outname)

        print("compiling %s" % ui_fname)

        f = open(pyfile, "w")
        uic.compileUi(ui_fname, f, execute=True)
        f.close()

        f = open(pyfile, "r")
        data = f.read()
        f.close()

        newdata = data
        for removal in self.REMOVALS:
            newdata = newdata.replace(removal, "")

        newdata = re.sub(r'_translate\((".*?"), (".*?")\)',
                         self.gettext_wrap, newdata, 0, re.DOTALL)

        for orig, new in self.REPLACEMENTS:
            newdata = newdata.replace(orig, new)

        newdata = version_fixes(newdata)

        if newdata != data:
            f = open(pyfile, "w")
            f.write(newdata)
            f.close()
        else:
            print("om_pyuic made no changes to the standard uic output!")

        return pyfile

    def get_ui_files(self):
        for ui_file in os.listdir(self.SRC_FOLDER):
            if re.match(".*.ui$", ui_file):
                yield ui_file

    def run(self, *args, **kwargs):
        print("compiling qt-designer files")
        for ui_file in self.get_ui_files():
            path = os.path.join(self.SRC_FOLDER, os.path.basename(ui_file))
            py_file = self.compile_ui(path, self.DEST_FOLDER)
            if py_file:
                print("created/updated py file", py_file)
        print("compiling resource file")
        p = subprocess.Popen(
            ["pyrcc5", "-o", RESOURCE_FILE,
             os.path.join(OM_PATH, "openmolar", "resources", "resources.qrc")]
        )
        p.wait()
        print("MakeUis Completed")


class Build(_build):
    '''
    re-implement to ensure that ui_files are called.
    '''

    def run(self, *args, **kwargs):
        make_uis = MakeUis(self.distribution)
        make_uis.run(*args, **kwargs)
        _build.run(self, *args, **kwargs)
        print("build completed")


class Clean(_clean):
    '''
    remove files created by configure
    '''

    def run(self, *args, **kwargs):
        print("running clean")
        for file_ in os.listdir(MakeUis.DEST_FOLDER):
            if file_.startswith("Ui"):
                os.remove(os.path.join(MakeUis.DEST_FOLDER, file_))
        if os.path.exists(RESOURCE_FILE):
            os.remove(RESOURCE_FILE)
        _clean.run(self, *args, **kwargs)


class Sdist(_sdist):

    '''
    overwrite distutils standard source code builder to remove
    extraneous code from version.py
    '''
    version_filepath = re.sub("\.pyc$", ".py", version.__file__)
    backup_version_filepath = version_filepath + "_orig"

    def run(self, *args, **kwargs):
        self.tear_down()
        _sdist.run(self, *args, **kwargs)
        self.clean_up()

    def tear_down(self):
        print("rewriting version.py")
        f = open(self.version_filepath, "r")
        new_data = ""
        add_line = True
        for line_ in f:
            if line_.startswith("VERSION ="):
                print("Forcing version number of '%s'" % VERSION)
                new_data += 'VERSION = "%s"\n\n\n' % VERSION
                add_line = False
            elif line_.startswith("if __name__"):
                add_line = True
            if add_line:
                new_data += line_

        shutil.move(self.version_filepath, self.backup_version_filepath)
        f = open(self.version_filepath, "w")
        f.write(new_data)
        f.close()

    def clean_up(self):
        os.remove(self.version_filepath)
        shutil.move(self.backup_version_filepath, self.version_filepath)


class InstallLocale(install_data):

    '''
    re-implement class distutils.install_data install_data
    compile binary translation files for gettext
    '''

    def run(self):
        print("COMPILING PO FILES")
        i18nfiles = []
        if not os.path.isdir("src/openmolar/locale/"):
            print("WARNING - language files are missing!")
        for po_file in glob.glob("src/openmolar/locale/*.po"):
            directory, file_ = os.path.split(po_file)
            lang = file_.replace(".po", "")
            mo_dir = os.path.join(directory, lang)
            try:
                os.mkdir(mo_dir)
                if IS_WINDOWS:
                    mo_dir = os.path.join(mo_dir, "LC_MESSAGES")
                    os.mkdir(mo_dir)
            except OSError:
                pass
            mo_file = os.path.join(mo_dir, "openmolar.mo")
            if not os.path.exists(mo_file) or newer(po_file, mo_file):
                cmd = 'msgfmt -o %s %s' % (mo_file, po_file)
                info('compiling %s -> %s' % (po_file, mo_file))
                if os.system(cmd) != 0:
                    info('Error while running msgfmt on %s' % po_file)

            destdir = os.path.join("share", "locale", lang)
            if IS_WINDOWS:
                destdir = os.path.join(destdir, "LC_MESSAGES")
            else:
                destdir = os.path.join("/usr", destdir)

            i18nfiles.append((destdir, [mo_file]))

        self.data_files.extend(i18nfiles)
        install_data.run(self)


class Test(Command):

    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self, *args, **kwargs):
        loader = unittest.TestLoader()
        tests = loader.discover(start_dir="src")
        result = unittest.TestResult()
        tests.run(result)
        print(result)


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
              'openmolar.settings',
              'openmolar.ptModules'],
    package_data={'openmolar': ['qt-designer/*.*',
                                'resources/icons/*.*',
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
        (USR + 'share/man/man1', ['bin/openmolar.1']),
        (USR + 'share/icons/hicolor/scalable/apps', ['bin/openmolar.svg']),
        (USR + 'share/applications', ['bin/openmolar.desktop']), ],
    cmdclass={'sdist': Sdist,
              'clean': Clean,
              'build': Build,
              'install_data': InstallLocale,
              'makeuis': MakeUis,
              'test': Test},
    scripts=['openmolar'],
)
