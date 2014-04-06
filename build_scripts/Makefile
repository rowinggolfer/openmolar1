define USEAGE 
This is the build script for openmolar tarballs.

USAGE
   make [options] target

TARGETS
   version
   git_tag
   tarball
   
EXAMPLES
	make NEW_VERSION=0.5.0-beta1 version
		this will update version.py, but will not update the git tag

	make git-tag
		this will tag the git repo with the version number set in version.py
		performs the following
		git tag -a v0.5.0-beta1 -m "v0.5.0-beta1" 

	make FORCE=true git-tag
		as above, but deleting any other reference to the tag
		performsthe following
		git tag -f -a v0.5.0-beta1 -m "v0.5.0-beta1"

	make tarball
		create a tarball
		needn't be a tagged (or even clean repo) for this

usual steps for a release would be as follows.
	make NEW_VERSION=0.5.1 version
	git commit -a
	git push
	make git-tag
	make tarball

endef
	
export USEAGE

PACKAGE=openmolar
CURRENT_MAKEFILE_LIST := $(MAKEFILE_LIST)
BUILD_SCRIPTS_DIR := $(abspath $(dir $(firstword $(CURRENT_MAKEFILE_LIST))))/
HEAD = $(shell $(BUILD_SCRIPTS_DIR)get_git_branch.py)/
BUILDS_DIR=$(HEAD)builds/

DIST_DIR=$(HEAD)dist/

#VERSION=`git describe | sed s/v//`
VERSION=`python $(HEAD)setup.py --version`

ifeq ($(NEW_VERSION), )
	NEW_VERSION=$(VERSION)
endif

ifeq ($(FORCE), true)
	FORCE_TAG=-f
endif


TARBALL = $(PACKAGE)-$(VERSION).tar.gz

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
	@echo "writing git tag  - if this fails and you haven't pushed tags to parent repo, try 'make FORCE=true git_tag'" 
	git tag $(FORCE_TAG) -a v$(NEW_VERSION) -m "$(NEW_VERSION)"

version:
	@echo "modding version.py"
	echo "sed -i s/VERSION = \".*\"/VERSION = \"$(NEW_VERSION)\"/ src/openmolar/settings/version.py"
	cd $(HEAD) ;\
		sed -i s/VERSION\ =\ \".*\"/VERSION\ =\ \"$(NEW_VERSION)\"/ src/openmolar/settings/version.py
	@echo "version updated"

tarball:
	echo "making  tarball (using setup.py sdist)"
	make clean_tmp
	cd $(HEAD) ;\
		python setup.py sdist ;\
	echo "tarball created!"
	mkdir -p $(BUILDS_DIR)
	echo "moving tarball to $(BUILDS_DIR)"
	cp -av $(DIST_DIR)$(TARBALL) $(BUILDS_DIR);
	@echo "tarball is located $(BUILDS_DIR)$(TARBALL)"

	@if [ -e "$(BUILDS_DIR)$(TARBALL)" ]; then echo "SUCCESS!"; fi
	
sign_tarball:
	cd $(BUILDS_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
	
	
