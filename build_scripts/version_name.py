#! /usr/bin/env python 

'''
read a changelog, and get the package name

parses a changelog with this 1st line
"openmolar-namespace (2.0.5+hg007-2~unstable0) unstable; urgency=low"

usage python version_name.py [DEBFOLDER]

output is "openmolar-namespace_2.0.5+hg007"
'''


import os
import re 
import sys

try:
    debian_directory = sys.argv[1]
except IndexError:
    sys.exit("version_name script called with no arguments") 

if not os.path.isdir(debian_directory):
    sys.exit("'%s' is not a directory"% debian_directory) 

filepath = os.path.join(debian_directory, "changelog")

try:
    f = open(filepath)
    data = f.read()
    f.close()

    matches = re.match("(.*) \((.*)-", data).groups()
    
    debname = "%s_%s"% (matches[0], matches[1])
    
    print (debname)

except:
    sys.exit("unable to parse changelog %s"% filepath)

