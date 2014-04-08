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
This module cleans and standardises the openmolar code.
autopep8 should be installed for full functionality

USEAGE is ./code_cleaner.py

OPTIONS:
     ALL      - modify all python files above the git repository
     no-pep8  - do not apply autopep8

EXAMPLES:
    ./code_cleaner.py
        this will check formatting of any file marked as new or modified
        in the git repo this should be done before each commit!

    ./code_cleaner.py ALL
        check and modify all files.

    ./code_cleaner.py ALL no-pep8
        does not apply the autopep8 tool, so only changes will be the
        shebang lines and license.
'''

import git
import logging
import os
import re
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("code_cleaner")

SHEBANG_LINE = "#! /usr/bin/env python"
ENCODING_LINE = "# -*- coding: utf-8 -*-"
LICENSE = '''
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


class CodeCleaner(object):

    '''
    A class which takes a git repository, and cleans up python code within.
    '''
    pep8 = True
    license_lines = set([])

    def __init__(self, repository, all_files=False):
        self.repo = repository
        self.root_path = self.repo.working_dir

        self.files = self._all_files if all_files else self._changed_files
        LOGGER.info("CodeCleaner object created")

    def _valid_file(self, filename):
        '''
        check to see if file is a python file
        '''
        if filename.endswith("resources_rc.py"):
            return False
        return filename == "openmolar" or re.match(".*.py$", filename)

    def _changed_files(self):
        '''
        use git to get only those files which have been altered.
        files object will be in this form

         M src/standalone_chart/om_chart.py
         M src/tests/appt_drag_test.py
        ?? build_scripts/code_cleaner.py

        so some regex work is required to pull the filename.
        '''
        files = self.repo.git.status("--porcelain")
        LOGGER.debug(files)
        for info in files.split("\n"):
            operation = info[:3].strip(" ")
            file_ = info[3:]
            if operation in ("M", "A") and self._valid_file(file_):
                yield os.path.join(self.root_path, file_)

    def _all_files(self):
        '''
        an iterator returning all files in child directories of the git repo
        which conform with _valid_file
        '''
        for root, dir_, files in os.walk(self.root_path):
            for file_ in files:
                if self._valid_file(file_):
                    file_path = os.path.join(root, file_)
                    yield file_path

    def autopep8(self, file_path):
        '''
        apply the wonderful autopep8 tool
        '''
        if self.pep8:
            LOGGER.debug("applying  autopep8")
            p = subprocess.Popen(
                ["autopep8", "-v", "--in-place", "-a", "-a", file_path])
            p.wait()

    def clean_files(self):
        count = 0
        changed = 0
        for file_path in self.files():
            count += 1
            LOGGER.info("cleaning %s" % file_path)

            self.autopep8(file_path)

            f = open(file_path)
            data = f.read()
            f.close()

            new_data = self._check_shebang(data)
            new_data = self._check_encoding(new_data)
            if not "compiled_uis" in file_path:
                new_data = self._change_license(new_data)

            if new_data != data:
                changed += 1
                f = open(file_path, "w")
                f.write(new_data)
                f.close()

        LOGGER.info("changed %d out of %d files" % (changed, count))

    def _check_shebang(self, data):
        '''
        apply the python shebang line if not present
        '''
        if data.split("\n")[0] == SHEBANG_LINE:
            return data
        return "%s\n%s" % (SHEBANG_LINE, data)

    def _check_encoding(self, data):
        '''
        apply the encoding shebang line if not present
        '''
        lines = data.split("\n")
        if lines[1] == ENCODING_LINE:
            return data
        lines.insert(1, ENCODING_LINE)
        return "\n".join(lines)

    def _change_license(self, data):
        '''
        remove any old license present, and replace with LICENSE
        '''
        lines = data.split("\n")
        removals = []
        for i, line in enumerate(lines[2:]):
            if line.startswith("#") or line.strip(" ") == "":
                removals.append(i + 2)
            else:
                break
        for i in sorted(removals, reverse=True):
            line = lines.pop(i)
            self.license_lines.add(line)

        for i, new_line in enumerate(LICENSE.split("\n")):
            lines.insert(i + 2, new_line)
        return "\n".join(lines)


def help_():
    '''
    print a help message and exit
    '''
    print __doc__
    sys.exit(0)

if __name__ == "__main__":
    if "help" in sys.argv:
        help_()
    LOGGER.setLevel(logging.DEBUG)
    repo = git.Repo(os.getcwd())
    cc = CodeCleaner(repo, "ALL" in sys.argv)
    cc.pep8 = not "no-pep8" in sys.argv
    cc.clean_files()

    LOGGER.warning(
        "removed the following license lines!%s" % "\n".join(cc.license_lines))
