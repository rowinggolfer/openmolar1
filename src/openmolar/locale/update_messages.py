#!/usr/bin/env python

'''
get all translatable strings into a single messages.pot
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
    
    subprocess.Popen([pygettext]+files)

if __name__ == "__main__":
    
    main(os.getcwd)
    