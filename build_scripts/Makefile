define USEAGE 
This is the build script for openmolar packages and tarballs.

USAGE
   make [options] target

OPTIONS
   DIST     (the target distribution - eg. unstable, testing, lucid etc.)
       default=unstable
       allowed values - anything.. 
       but if building a deb, have a pbuilder environment with this name
   NEW_CHANGELOG (run a gui to modify the changelog)
       default=true

TARGETS
   version
   tarball
   deb_src
   deb_binary
   all_tarballs
   all_deb_srcs
   all_deb_binaries

EXAMPLES are available.
	make examples
endef

define EXAMPLES
EXAMPLES
make tarball
	create a tarball

make changelog
	update the changelog in the template debian directory

make deb DIST=stable
	debian packages for debian stable (squeeze)
make deb DIST=precise 
	create a debian binary package for ubuntu precise (12.04).
make debs 
	makes debian package for all distributions and architectures

endef
	
export USEAGE
export EXAMPLES

ifeq ($(DIST), )
	DIST=unstable
endif

ifeq ($(NEW_CHANGELOG), )
	NEW_CHANGELOG=true
endif

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

###################  Debian Packaging Stuff ####################################
#                                                                              #
DEB_CONF_DIR=$(BUILD_SCRIPTS_DIR)debian_packaging/dh_python2/debian/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/

DEBDISTS = unstable testing stable oldstable saucy raring quantal precise

CHANGELOG=$(DEB_BUILDS_DIR)$(shell ls -t $(DEB_BUILDS_DIR) | grep changes | head -n1)

#                                                                              #
##################  Debian packaging ends  #####################################


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
	git tag -a v$(NEW_VERSION) -m "$(NEW_VERSION)"

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
	mkdir -p $(TARBALL_DIR)
	echo "moving tarball to $(TARBALL_DIR)"
	cp -av $(DIST_DIR)$(TARBALL) $(TARBALL_DIR);
	@echo "tarball is located $(TARBALL_DIR)$(TARBALL)"

	@if [ -e "$(TARBALL_DIR)$(TARBALL)" ]; then echo "SUCCESS!"; fi
	
sign_tarball:
	cd $(TARBALL_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
	
	
changelog:
	# call my changelog gui
	@echo $(BUILD_SCRIPTS_DIR)deb_maker.py -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) 
	$(BUILD_SCRIPTS_DIR)deb_maker.py -p$(PACKAGE) -s$(TARBALL_DIR) -d$(DEB_CONF_DIR)
	
deb:	
	make clean_tmp

	@echo "Making debian packages target distro = $(DIST)"
		
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then make changelog; fi
	
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxf $(TARBALL); \
	mv $(TARBALL) `python $(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`.orig.tar.gz 
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	echo "modding changelog" ;\
	sed -i s/__DIST__/$(DIST)/g debian/changelog ;\
	sudo pdebuild --buildresult $(DEB_BUILDS_DIR) --pbuilderroot "sudo DIST=$(DIST)"
	
debsign:
	debsign $(DEB_BUILDS_DIR)*$(VERSION)*.changes -kF230408E 
	
debsigns:
	#make debsign DIST=<unstable|testing|stable|raring|quantal|precise|lucid> 
	
	$(foreach dist,$(DEBDISTS), \
		make debsign DIST=$(dist) ;\
	)
	
notes:
	#pdebuild --architecture <i386|amd64>  --buildresult /tmp --pbuilderroot "sudo DIST=<unstable|stable|testing|raring|quantal|precise|lucid> ARCH=<i386|amd64>"
	
debs:
	@echo "making all debian based packages.. first we need to update the changelogs for the 2 build systems"
	make changelog
	make git_tag
	git commit -a -m "versioning"

	@if [ ! -e "$(TARBALL_DIR)$(TARBALL)" ]; then make tarball; fi

	$(foreach dist,$(DEBDISTS), \
		make deb DIST=$(dist) NEW_CHANGELOG=False;\
	) 
	
pushdeb:
	cd ~/www/repos/apt/debian ;\
	reprepro include $(DIST) $(CHANGELOG) ; \
	#reprepro export
	
pushdebs:
	@echo "updating the local repo"
	$(foreach dist,$(DEBDISTS), \
		make DIST=$(dist) pushdeb; \
	)
	cd ~/www/repos/apt/debian ;\
	reprepro export
	
update_pbuilder:
	$(foreach dist, $(DEBDISTS), \
		sudo DIST=${dist} ARCH=amd64 pbuilder --update --architecture amd64 \
		--distribution ${dist} --http-proxy http://localhost:3142 ; \
	)
	
create_pbuilder:
	$(foreach dist, $(DEBDISTS), \
		sudo DIST=${dist} ARCH=amd64 pbuilder --create --architecture amd64 \
		--distribution ${dist} --http-proxy http://localhost:3142 ; \
	)

test:
	@echo chosen package $(PACKAGE)
	@echo targetting distro $(DIST)
	@if [ $(NEW_CHANGELOG) = 'true' ]; then \
		echo changelog WILL be updated; \
	fi
	@echo debconfdir = $(DEB_CONF_DIR)
	@echo Head = $(HEAD)
	@echo Dist = $(DIST)
	@echo DEB_BUILDS_DIR = $(DEB_BUILDS_DIR)
	@echo changelog = $(CHANGELOG)
	
