define USEAGE 
This is the build script for openmolar packages and tarballs.

USAGE
   make [options] target

OPTIONS
   DIST     (the target distribution - eg. unstable, testing, lucid etc.) 
       default=unstable
       allowed values - anything.. 
       but if building a deb, have a pbuilder environment with this name    
   DEBHELPER     (specifies with python system to use for debian source packages)                    
       allowed=py_central, dh_python2
       default=dh_python2
   NEW_CHANGELOG (run a gui to modify the changelog)
       default=true

TARGETS
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
	create a tarball for the default package (openmolar-namespace)   
make tarball SUFFIX=client
	create a tarball for openmolar-client   
make all_tarballs
	create tarballs for ALL suffixes

make changelog
	update the changelog in the template debian directory
make changelog DEBHELPER=py_central
	update the changelog in the template debian directory for py_central build system (which is deprecated, but necessary for lucid)

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

ifeq ($(DEBHELPER), )
	DEBHELPER=dh_python2
endif

#in case I forget!!
ifeq ($(DIST), lucid)
	DEBHELPER=py_central
endif

ifeq ($(NEW_CHANGELOG), )
	NEW_CHANGELOG=true
endif

PACKAGE=openmolar

HEAD=$(HOME)/openmolar/openmolar/
BUILD_SCRIPTS_DIR = $(HEAD)/build_scripts/
BUILDS_DIR=$(HEAD)builds/

DIST_DIR=$(HEAD)dist/

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py`

TARBALL = $(PACKAGE)-$(VERSION).tar.gz
TARBALL_DIR=$(HEAD)builds/tarballs/

TMP_DIR=$(HEAD)tmp/

###################  Debian Packaging Stuff ####################################
#                                                                              #
DEB_CONF_DIR=$(HEAD)build_scripts/debian_packaging/$(DEBHELPER)/debian/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/

DEBDISTS = unstable testing stable precise lucid
DEBHELPERS= py_central dh_python2

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

update_version:
	bzr version-info --format=python > $(HEAD)src/openmolar/settings/_version.py

tarball:
	echo "making  tarball"
	make update_version
	mkdir -p $(TARBALL_DIR)
	cd $(HEAD) ;\
		python setup.py sdist ;\
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
	@if [ ! -e "$(TARBALL_DIR)$(TARBALL)" ]; then make tarball; fi
	
	make clean_tmp

	@echo "Making debian packages target distro = $(DIST)"
		
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then make changelog; fi
	
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxvf $(TARBALL); \
	mv $(TARBALL) `$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`.orig.tar.gz 
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	echo "modding changelog" ;\
	sed -i s/__DIST__/$(DIST)/g debian/changelog ;\
	sudo pdebuild --buildresult $(DEB_BUILDS_DIR) --pbuilderroot "sudo DIST=$(DIST)"
	
	make debsigns
	
debsign:
	debsign $(DEB_BUILDS_DIR)*$(VERSION)*.changes -kF230408E 
	
debsigns:
	#make debsign DIST=<unstable|testing|stable|precise|lucid> 
	
	$(foreach dist,$(DEBDISTS), \
		make debsign DIST=$(dist) ;\
	) 
	
	
notes:
	#pdebuild --architecture <i386|amd64>  --buildresult /tmp --pbuilderroot "sudo DIST=<unstable|stable|testing|hardy|lucid|natty|oneiric|precise> ARCH=<i386|amd64>"
	
debs:
	@echo "making all debian based packages.. first we need to update the changelogs for the 2 build systems"
	
	#make changelog DEBHELPER=<dh_python2|py_central>
	$(foreach var,$(DEBHELPERS), make changelog DEBHELPER=$(var);)
	
	#make deb DIST=<unstable|testing|stable|precise|lucid> NEW_CHANGELOG=False 
	$(foreach dist,$(DEBDISTS), \
		make deb DIST=$(dist) NEW_CHANGELOG=False;\
	) 
	
	#make debsign DIST=<unstable|testing|stable|precise|lucid> 
	$(foreach var,$(DEBDISTS), make debsign DIST=$(var);) 
	
pushdebs:
	@echo "updating the local repo"
	$(foreach dist,$(DEBDISTS), \
		cd ~/www/repos/apt/debian ;\
		reprepro include $(dist) $(HEAD)builds/debs/$(dist)/*$(VERSION)*.changes ; \
	) 
	
	
test:
	@echo "chosen package $(PACKAGE)"
	@echo "targetting distro $(DIST)"
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then \
		echo "changelog WILL be updated"; \
	fi
	@echo "debconfdir = $(DEB_CONF_DIR)"
	@echo "Dist = $(DIST)"
	
