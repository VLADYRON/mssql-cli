# RPM spec file for mssql-cli
# Definition of macros used - https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros

# .el7.centos -> .el7
%if 0%{?rhel} == 7
  %define dist .el7
%endif

%define name           mssql-cli
%define release        1%{?dist}
%define version        0.10.0
%define repo_path      %{getenv:REPO_PATH}
%define python_url     https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
%define cli_lib_dir    %{_libdir}/mssql-cli

Summary:        Microsoft SQL Server CLI
License:        BSD-3
Name:           %{name}
Version:        %{version}
Release:        %{release}
Url:            https://github.com/dbcli/mssql-cli/blob/master/doc/installation_guide.md
BuildArch:      x86_64
Requires:       python

BuildRequires:  gcc
BuildRequires:  python
BuildRequires:  libffi-devel
BuildRequires:  python-devel
BuildRequires:  openssl-devel

%description
    We’re excited to introduce mssql-cli, a new and interactive command line query tool for SQL Server.
    This open source tool works cross-platform and proud to be a part of the dbcli.org community.


%prep
# Download, Extract Python3
python_archive=$(mktemp)
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz -qO $python_archive
tar -xvzf $python_archive -C %{_builddir}

%install
# clean any previous make files
make clean || echo "Nothing to clean"

# Build Python from source
%{_builddir}/*/configure --srcdir %{_builddir}/* --prefix %{buildroot}%{cli_lib_dir}
make
make install

# Build mssql-cli wheel from source.
# Set env var to ensure build.py uses the python we built from source.
export CUSTOM_PYTHON=$source_dir/python_env/bin/python3
export CUSTOM_PIP=$source_dir/python_env/bin/pip3

source_dir=%{repo_path}
dist_dir=$(mktemp -d)

cd %source_dir
%{buildroot}%{cli_lib_dir}/bin/python3 build.py build
cd -

# Install mssql-cli
dist_dir=%source_dir/dist
all_modules=`find $dist_dir -name "*.whl"`
%{buildroot}%{cli_lib_dir}/bin/pip3  install $all_modules

# Fix up %{buildroot} appearing in some files...
for d in %{buildroot}%{cli_lib_dir}/bin/*; do perl -p -i -e "s#%{buildroot}##g" $d; done;

# Create executable
mkdir -p %{buildroot}%{_bindir}
printf "if [ -z ${PYTHONIOENCODING+x} ]; then export PYTHONIOENCODING=utf8; fi" > %{buildroot}%{_bindir}/mssql-cli
printf '#!/usr/bin/env bash\n%{cli_lib_dir}/bin/python3 -Esm mssqlcli.main "$@"' > %{buildroot}%{_bindir}/mssql-cli


%files
# Include mssql-cli directory which includes it's own python.
# Include executable mssql-cli.
%attr(-,root,root) %{cli_lib_dir}
%attr(0755,root,root) %{_bindir}/mssql-cli
