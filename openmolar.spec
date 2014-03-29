%define name openmolar
%define version 0.1.9
%define unmangled_version 0.1.9
%define release 1

Summary: Open Source Dental Practice Management Software
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPL v3
Group: Office
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
BuildRequires: python-devel, -post-build-checks
Requires: PyQt4, MySQL-python
Vendor: Neil Wallace <rowinggolfer@googlemail.com>
Url: https://launchpad.net/openmolar

%description
Dental Practice Management Suite, using a Mysql database server to maintain patient records, accounts, and correspondence.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install  --prefix=/usr --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Sun Feb 7 2010 rowinggolfer@googlemail.com
- packaged openmolar version 0.1.9
