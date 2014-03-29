#!/usr/bin/env python
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.


'''
get all translatable strings into a single messages.pot
requires pygettext available on the command line - i.e. NOT windows friendly.
'''

import os
import subprocess

def source_files(PATH):
    retarg = []
    for root, dir, files in os.walk(os.path.dirname(PATH)):
        for name in files:
            if name.endswith('.py'):
                retarg.append(os.path.abspath(os.path.join(root, name)))
    return retarg

def main(PATH):
    files = source_files(os.path.dirname(PATH))
    print "%d py files found"% len(files)
    print "using pygettext to create a messages.pot.....",
    pr = subprocess.Popen(["pygettext"]+files)
    pr.wait()
    print "finished"

if __name__ == "__main__":

    main(os.getcwd())
