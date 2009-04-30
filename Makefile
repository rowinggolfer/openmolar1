# Copyright (C) 2009 Bryan Harris
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# A relatively simple Makefile to assist in building parts of bzr. Mostly for
# building documentation, etc.


### Core Stuff ###

PYTHON=python

#.PHONY: all clean install pyflakes

all: clean build

build: clean
	@echo "Building openMolar"
	$(PYTHON) setup.py build

package: clean
	@echo "Building generic debian package"
	touch qt-designer/__init__.py
	touch resources/__init__.py
	$(PYTHON) setup.py sdist

install: 
	@echo "Building and installing openMolar to $(DESTDIR)"
	$(PYTHON) setup.py install --prefix "$(DESTDIR)"  


# Run Python style checker (apt-get install pyflakes)
#
# Note that at present this gives many false warnings, because it doesn't
# know about identifiers loaded through lazy_import.
pyflakes:
	pyflakes openmolar

pyflakes-nounused:
	# There are many of these warnings at the moment and they're not a
	# high priority to fix
	pyflakes openmolar | grep -v ' imported but unused'

clean:
	$(PYTHON) setup.py clean
	rm -f MANIFEST
	-find . -name "*.pyc" -o -name "*.pyo" -o -name "*.so" | xargs rm -f
