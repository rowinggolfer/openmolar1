#!/usr/bin/env python

from distutils.command.install_data import install_data
from distutils.core import setup
from distutils.dep_util import newer
from distutils.log import info

import glob
import os
import re

def get_version():
    '''
    returns a string with in the format X.Y.Z+bzr04d
    '''
    version = "0.2.2"
    try:
        from bzrlib import branch
        revno = branch.Branch.open(".").revno()
        return "%s+bzr%04d"% (version, revno)
    except Exception as exc:
        print ("Warning - unable to get bzr number")
    return version

class InstallData(install_data):
    def run(self):
        self.data_files.extend(self._compile_po_files())
        install_data.run(self)

    def _compile_po_files(self):
        print "COMPILING PO FILES"
        i18nfiles = []
        if not os.path.isdir("src/openmolar/locale/"):
            print "WARNING - language files are missing!"
        for po in glob.glob("src/openmolar/locale/*.po"):
            directory, file = os.path.split(po)
            lang = file.replace(".po","")
            mo = os.path.join(directory, lang)
            try:
            	os.mkdir(mo)
            except OSError:
                pass
            mo = os.path.join(mo, "openmolar.mo")
            if not os.path.exists(mo) or newer(po, mo):
                cmd = 'msgfmt -o %s %s' % (mo, po)
                info ('compiling %s -> %s' % (po, mo))
                if os.system(cmd) != 0:
                    info('Error while running msgfmt on %s'% po)

            destdir = os.path.join ("/usr","share", "locale", lang,
            "LC_MESSAGES")

            i18nfiles.append((destdir, [mo]))
        return i18nfiles

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

setup(
    name = 'openmolar',
    version = get_version(),
    description = 'Open Source Dental Practice Management Software',
    author = 'Neil Wallace',
    author_email = 'rowinggolfer@googlemail.com',
    url = 'https://launchpad.net/openmolar',
    license = 'GPL v3',
    package_dir = {'openmolar' : 'src/openmolar'},
    packages = ['openmolar',
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
                'openmolar.qt4gui.printing',
                'openmolar.qt4gui.tools',
                'openmolar.settings',
                'openmolar.ptModules'],
    package_data = {'openmolar' : ['resources/icons/*.*',
                                    'resources/teeth/*.png',
                                    'resources/*.*',
                                    'html/*.*',
                                    'html/images/*.*',
                                    'html/firstrun/*.*',] },
    data_files = [
        ('/usr/share/icons/hicolor/scalable/apps', ['bin/openmolar.svg']),
        ('/usr/share/applications', ['bin/openmolar.desktop']),],
    cmdclass = {'install_data': InstallData},
    scripts = ['openmolar'],
    )
