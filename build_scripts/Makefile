define USEAGE 
This is the build script for openmolar tarballs.

USAGE
   make [options] target

TARGETS
   version
   tarball
   deb_src
   
EXAMPLES are available.
	make examples
endef

define EXAMPLES
EXAMPLES
make tarball
	create a tarball

endef
	
export USEAGE
export EXAMPLES

PACKAGE=openmolar
CURRENT_MAKEFILE_LIST := $(MAKEFILE_LIST)
BUILD_SCRIPTS_DIR := $(abspath $(dir $(firstword $(CURRENT_MAKEFILE_LIST))))/
HEAD = $(shell $(BUILD_SCRIPTS_DIR)get_git_branch.py)/
BUILDS_DIR=$(HEAD)builds/

DIST_DIR=$(HEAD)dist/

#VERSION=`git describe | sed s/v//`
VERSION=`$(BUILD_SCRIPTS_DIR)get_version.py`

ifeq ($(NEW_VERSION), )
	NEW_VERSION=$(VERSION)
endif

TARBALL = $(PACKAGE)-$(VERSION).tar.gz
TARBALL_DIR=$(HEAD)builds/tarballs/

TMP_DIR=$(HEAD)tmp/

.phony:
	make help

help:
	@echo "$$USEAGE"

examples:
	@echo "$$EXAMPLES"
	
clean_tmp:
	mkdir -p $(TMP_DIR)
	rm -rf $(TMP_DIR)*

resources:
	pyrcc4 -py2 $(HEAD)/src/openmolar/resources/resources.qrc > $(HEAD)/src/openmolar/qt4gui/resources_rc.py

ui_files:
	./om_pyuic4.py

clean_codebase:
	./code_cleaner.py

git_tag:
	git tag $(FORCE_TAG) -a v$(NEW_VERSION) -m "$(NEW_VERSION)"

version:
	@echo "modding version.py"
	echo "sed -i s/VERSION = \".*\"/VERSION = \"$(NEW_VERSION)\"/ src/openmolar/settings/version.py"
	cd $(HEAD) ;\
		sed -i s/VERSION\ =\ \".*\"/VERSION\ =\ \"$(NEW_VERSION)\"/ src/openmolar/settings/version.py
	@echo "version updated"

tarball:
	echo "making  tarball (using setup.py sdist)"
	make FORCE_TAG=-f git_tag
	make clean_tmp
	cd $(HEAD) ;\
		python setup.py sdist ;\
	echo "tarball created!"
	mkdir -p $(TARBALL_DIR)
	echo "moving tarball to $(TARBALL_DIR)"
	cp -av $(DIST_DIR)$(TARBALL) $(TARBALL_DIR);
	@echo "tarball is located $(TARBALL_DIR)$(TARBALL)"

	@if [ -e "$(TARBALL_DIR)$(TARBALL)" ]; then echo "SUCCESS!"; fi
	
sign_tarball:
	cd $(TARBALL_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
	
	
