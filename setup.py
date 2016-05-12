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
see https://docs.python.org/3/distutils/setupscript.html for explanation
'''

from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as _sdist
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.command.build_py import build_py as _build_py
from distutils.command.install import install as _install
from distutils import dir_util
from distutils.core import setup
from distutils.core import Command
from distutils.log import info, warn

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

DATA_FILES = []  # warning if DATA_FILES == [], install_data doesn't get called

# il8n_DIR refers to the location in which compiled gettext translation files
# are put during install.
# on linux systems, the default location is /usr/share/locale
# On Windows the default gettext path is within the python path
# eg C:\\Python34\share\locale which is a little nasty IMO.
# I therefore force the path for gettext to be under the %ProgramFiles%
# directory.

if platform.system() == 'Windows':
    RESOURCES_DIR = os.path.join(os.environ.get("ProgramFiles"), "openmolar")
    il8n_DIR = os.path.join(RESOURCES_DIR, "locale")
    SCRIPTS = ['win_openmolar.pyw']
else:
    RESOURCES_DIR = os.path.join("/usr", "share", "openmolar")
    il8n_DIR = os.path.join("/usr", "share", "locale")
    for dir_, files in (('share/icons/hicolor/scalable/apps',
                         ['bin/openmolar.svg']),
                        ('share/applications', ['bin/openmolar.desktop']),
                        ('share/man/man1', ['bin/openmolar.1'])):
        DATA_FILES.append((dir_, [os.path.abspath(p) for p in files]))
    SCRIPTS = ['openmolar']


DATA_FILES.append(
    (os.path.join(RESOURCES_DIR, "locale", "sources"),
     [os.path.abspath(p) for p in glob.glob('src/openmolar/locale/*.po*')]))

for root, dirs, files in os.walk(os.path.abspath('src/openmolar/resources')):
    rootdirs = root.split(os.path.sep)
    subdirs = rootdirs[rootdirs.index("resources"):]
    dest_dir = os.path.join(RESOURCES_DIR, *subdirs)
    DATA_FILES.append((dest_dir, [os.path.join(root, f) for f in files]))


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
    RESOURCE_FILE = RESOURCE_FILE

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

    def compile_ui(self, ui_fname):

        name = os.path.basename(ui_fname)
        outname = "Ui_%s.py" % name.rstrip(".ui")
        pyfile = os.path.join(self.DEST_FOLDER, outname)

        info("compiling %s" % ui_fname)

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
            info("om_pyuic made no changes to the standard uic output!")

        return pyfile

    def get_ui_files(self):
        for ui_file in os.listdir(self.SRC_FOLDER):
            if re.match(".*.ui$", ui_file):
                yield ui_file

    def run(self, *args, **kwargs):
        info("compiling qt-designer files")
        for ui_file in self.get_ui_files():
            path = os.path.join(self.SRC_FOLDER, os.path.basename(ui_file))
            py_file = self.compile_ui(path)
            if py_file:
                info("created/updated py file %s", py_file)
        qrc_path = os.path.join(OM_PATH, "openmolar", "resources",
                                "resources.qrc")
        info("compiling resource file %s from source %s", self.RESOURCE_FILE,
             qrc_path)
        p = subprocess.Popen(["pyrcc5", "-o", self.RESOURCE_FILE, qrc_path])
        p.wait()
        info("MakeUis Completed")


class AlterVersion(object):
    '''
    openmolar version file is tweaked on install or sdist.
    extraneous code is removed.
    '''
    version_filepath = re.sub(r"\.pyc$", ".py", version.__file__)
    backup_version_filepath = version_filepath + "_orig"

    def change(self):
        '''
        the git repository version of openmolar contains some hooks into git
        these should be removed for a source or binary build.
        '''
        print("rewriting version.py")
        f = open(self.version_filepath, "r")
        new_data = ""
        add_line = True
        for line_ in f:
            if line_.startswith("try:"):
                print("Forcing version number of '%s'" % VERSION)
                new_data += 'VERSION = "%s"\n\n\n' % VERSION
                add_line = False
            elif line_.startswith("if __name__"):
                add_line = True
            if add_line:
                new_data += line_
        f.close()

        shutil.move(self.version_filepath, self.backup_version_filepath)
        f = open(self.version_filepath, "w")
        f.write(new_data)
        f.close()

    def restore(self):
        '''
        revert the changes made by AlterVersion.change()
        fails silently if no backup file is present
        '''
        print("restoring version.py")
        try:
            shutil.move(self.backup_version_filepath, self.version_filepath)
        except FileNotFoundError:
            pass

    def test(self):
        '''
        check that running change, followed by restore doesn't alter the repo.
        '''
        self.change()
        self.restore()


class WindowsScript(object):
    '''
    the openmolar script doesn't work well on windows as
    from import openmolar import main is a namespace munge with
    an executable named simply "openmolar"
    move it to win_openmolar.pyw and all is well :)
    '''

    def move_executable(self):
        if platform.system() == 'Windows':
            print("Moving the executable to win_openmolar.pyw")
            shutil.copy('openmolar', 'win_openmolar.pyw')

    def remove_executable(self):
        print("REMOVING win_openmolar.pyw")
        try:
            os.remove('win_openmolar.pyw')
        except FileNotFoundError:
            info("win_openmolar.pyw NOT removed (file not present)")

    def test(self):
        '''
        check that running change, followed by restore doesn't alter the repo.
        '''
        self.move_executable()
        self.remove_executable()


class BuildPy(_build_py):
    '''
    re-implement build_py so that the Ui files are compiled.
    '''

    def run(self, *args, **kwargs):
        _build_py.run(self, *args, **kwargs)
        make_uis = MakeUis(self.distribution)

        qt4gui_path = os.path.join(self.get_package_dir("openmolar"), "qt4gui")
        make_uis.DEST_FOLDER = os.path.join(qt4gui_path, "compiled_uis")
        make_uis.RESOURCE_FILE = os.path.join(qt4gui_path, "resources_rc.py")
        make_uis.run(*args, **kwargs)
        info("build_py completed")


class Build(_build):
    '''
    re-implement to ensure that ui_files are called.
    '''

    def setup(self):
        '''
        before building, modify the version.py file
        create a windows executable if necessary
        '''
        alter_version = AlterVersion()
        alter_version.change()
        win_script = WindowsScript()
        win_script.move_executable()

    def tear_down(self):
        '''
        after building, return the repo to unaltered state
        '''
        alter_version = AlterVersion()
        alter_version.restore()
        win_script = WindowsScript()
        win_script.remove_executable()

    def locale_build(self):
        '''
        I want python setup.py build to create the compiled gettext mo files.
        The primary driver is the ability to create a windows msi installer
        which includes these files.
        '''
        info("COMPILING PO FILES (gettext translations)")
        if not os.path.isdir("src/openmolar/locale/"):
            warn("WARNING - language files are missing!")
        locale_dir = os.path.join(self.build_base, "locale")
        try:
            dir_util.remove_tree(locale_dir)
        except Exception:
            warn("unable to remove directory %s", locale_dir)
        self.mkpath(locale_dir)
        for po_file in glob.glob("src/openmolar/locale/*.po"):
            file_ = os.path.split(po_file)[1]
            lang = file_.replace(".po", "")
            os.mkdir(os.path.join(locale_dir, lang))
            mo_file = os.path.join(locale_dir, lang, "openmolar.mo")
            commands = ["msgfmt", "-o", mo_file, po_file]
            info('executing %s' % " ".join(commands))
            try:
                p = subprocess.Popen(commands)
                p.wait()
            except IOError:
                info('Error while running msgfmt on %s - '
                     'perhaps msgfmt (gettext) is not installed?' % po_file)

    def run(self, *args, **kwargs):
        '''
        compile ui files and move all files into build dir
        also compile gettext mo files.
        '''

        _build.run(self, *args, **kwargs)
        self.locale_build()

        info("build completed")


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
        win_script = WindowsScript()
        win_script.remove_executable()


class Sdist(_sdist):

    '''
    re-implement distutils standard source code builder
    '''

    def run(self, *args, **kwargs):
        alter_version = AlterVersion()
        alter_version.change()
        _sdist.run(self, *args, **kwargs)
        alter_version.restore()


class Install(_install):

    '''
    re-implement distutils standard source code builder
    '''

    def run(self, *args, **kwargs):
        alter_version = AlterVersion()
        alter_version.change()
        win_script = WindowsScript()
        win_script.move_executable()
        _install.run(self, *args, **kwargs)
        alter_version.restore()
        win_script.remove_executable()


class InstallData(install_data):

    '''
    re-implement class distutils.install_data install_data
    compile binary translation files for gettext
    '''

    def run(self):
        i18nfiles = []
        for root, dirs, files in os.walk(os.path.join("build", "locale")):
            for file_ in files:
                if file_ == "openmolar.mo":
                    lang = os.path.split(root)[1]
                    destdir = os.path.join(il8n_DIR, lang, "LC_MESSAGES")
                    mo_file = os.path.join(root, file_)
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


if __name__ == "__main__":

    # I need to import this module so the windows installer can access the
    # data files attribute
    # hence the __name__ == "__main__" trick

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
        data_files=DATA_FILES,
        cmdclass={'sdist': Sdist,
                  'clean': Clean,
                  'build_py': BuildPy,
                  'build': Build,
                  'install': Install,
                  'install_data': InstallData,
                  'makeuis': MakeUis,
                  'test': Test},
        scripts=SCRIPTS,
    )
