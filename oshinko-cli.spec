#debuginfo not supported with Go
%global debug_package %{nil}
# modifying the Go binaries breaks the DWARF debugging
%global __os_install_post %{_rpmconfigdir}/brp-compress

%global gopath      %{_datadir}/gocode
%global import_path github.com/radanalyticsio/oshinko-cli

# docker_version is the version of docker requires by packages
%global docker_version 1.12
%global golang_version 1.4
# %commit is intended to be set by tito custom builders provided
# in the .tito/lib directory. The value in this spec file will not be kept up to date.
%{!?commit:
%global commit b510c5f61d28fbe50731d5327078da19527f2ce5
}
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%if 0%{?skip_build}
%global do_build 0
%else
%global do_build 1
%endif
%if 0%{?skip_prep}
%global do_prep 0
%else
%global do_prep 1
%endif
%if 0%{?skip_dist}
%global package_dist %{nil}
%else
%global package_dist %{dist}
%endif

%if 0%{?fedora} || 0%{?epel}
%global need_redistributable_set 0
%else
# Due to library availability, redistributable builds only work on x86_64
%ifarch x86_64
%global need_redistributable_set 1
%else
%global need_redistributable_set 0
%endif
%endif
%{!?make_redistributable: %global make_redistributable %{need_redistributable_set}}

%global package_name oshinko-cli
%global product_name radanalytics.io

%{!?version: %global version v0.5.3}
%{!?release: %global release 1}
%{!?gitver: %global gitver %{name}-%{version}-%{release} }

Name:           %{package_name}
Version:        0.5.4
Release:        1
Summary:        Spark Cluster Management for OpenShift
License:        ASL 2.0
URL:            https://%{import_path}

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:  x86_64 aarch64 ppc64le s390x
%endif

Source0:        https://%{import_path}/archive/%{commit}/%{name}-%{version}.tar.gz
BuildRequires:  golang >= %{golang_version}

#
# The following Bundled Provides entries are populated automatically by the
# OpenShift Origin tito custom builder found here:
#   https://github.com/openshift/origin/blob/master/.tito/lib/origin/builder/
#
# These are defined as per:
# https://fedoraproject.org/wiki/Packaging:Guidelines#Bundling_and_Duplication_of_system_libraries
#
### AUTO-BUNDLED-GEN-ENTRY-POINT

%description
The oshinko client application manages Apache Spark clusters on OpenShift. 
The client application also consists of a REST server (oshinko-rest) and 
is designed to run in an OpenShift project.

%prep
%if 0%{do_prep}
%setup -q
%endif

%build
%if 0%{do_build}
%if 0%{make_redistributable}
# Create Binaries for all supported arches
make build tag=%{gitver}
hack/build-go.sh vendor/github.com/onsi/ginkgo/ginkgo
%else
# Create Binaries only for building arch
%ifarch x86_64
  BUILD_PLATFORM="linux/amd64"
%endif
%ifarch %{ix86}
  BUILD_PLATFORM="linux/386"
%endif
%ifarch ppc64le
  BUILD_PLATFORM="linux/ppc64le"
%endif
%ifarch %{arm} aarch64
  BUILD_PLATFORM="linux/arm64"
%endif
%ifarch s390x
  BUILD_PLATFORM="linux/s390x"
%endif
OS_ONLY_BUILD_PLATFORMS="${BUILD_PLATFORM}" make build tag=%{gitver}
OS_ONLY_BUILD_PLATFORMS="${BUILD_PLATFORM}" hack/build-go.sh vendor/github.com/onsi/ginkgo/ginkgo
%endif

# Generate man pages
hack/generate-docs.sh
%endif

%install

PLATFORM="$(go env GOHOSTOS)/$(go env GOHOSTARCH)"
install -d %{buildroot}%{_bindir}

# Install linux components
echo "+++ INSTALLING %{name}"
install -p -m 755 _output/local/bin/${PLATFORM}/%{name} %{buildroot}%{_bindir}/oshinko

# Install tests
install -d %{buildroot}%{_libexecdir}/%{name}
install -p -m 755 _output/local/bin/${PLATFORM}/extended.test %{buildroot}%{_libexecdir}/%{name}/
install -p -m 755 _output/local/bin/${PLATFORM}/ginkgo %{buildroot}%{_libexecdir}/%{name}/

%if 0%{?make_redistributable}
# Install client executable for windows and mac
install -d %{buildroot}%{_datadir}/%{name}/{linux,macosx,windows}
install -p -m 755 _output/local/bin/linux/amd64/oc %{buildroot}%{_datadir}/%{name}/linuxa/oshinko
install -p -m 755 _output/local/bin/darwin/amd64/oc %{buildroot}/%{_datadir}/%{name}/macosx/oshinko
install -p -m 755 _output/local/bin/windows/amd64/oc.exe %{buildroot}/%{_datadir}/%{name}/windows/oshinko.exe
%endif


install -d -m 0755 %{buildroot}%{_unitdir}

# Install man1 man pages
install -d -m 0755 %{buildroot}%{_mandir}/man1
install -m 0644 docs/man/man1/* %{buildroot}%{_mandir}/man1/

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

# Install bash completions
install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d/
echo "+++ INSTALLING BASH COMPLETIONS FOR %{name} "
%{buildroot}%{_bindir}/%{name} completion bash > %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}
chmod 644 %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

%files
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%{_sharedstatedir}/%{name}
%{_sysconfdir}/bash_completion.d/%{name}
%defattr(-,root,root,0700)
%{_mandir}/man1/%{name}*

%pre

%if 0%{?make_redistributable}
%dir %{_datadir}/%{name}/linux/
%dir %{_datadir}/%{name}/macosx/
%dir %{_datadir}/%{name}/windows/
%{_datadir}/%{name}/linux/oshinko
%{_datadir}/%{name}/macosx/oshinko
%{_datadir}/%{name}/windows/oshinko.exe
%endif

%changelog
* Tue Nov 28 2017 Peter MacKinnon <pmackinn@redhat.com> 0.5.4-1
- Clean up os_git_var refs in spec file (pmackinn@redhat.com)

* Tue Nov 28 2017 Peter MacKinnon <pmackinn@redhat.com> 0.5.3-1
- Remove ldflags lookups since we set that directly in build.sh
  (pmackinn@redhat.com)

* Tue Nov 28 2017 Peter MacKinnon <pmackinn@redhat.com> 0.5.2-1
- Remove other git_var functions (pmackinn@redhat.com)
- Remove OS_ var refs from .tito (pmackinn@redhat.com)
- Remove OS_ROOT path dep (pmackinn@redhat.com)

* Fri Nov 17 2017 Peter MacKinnon <pmackinn@redhat.com> 0.5.1-1
- tito tagging 

* Thu Nov 16 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-6
- More wrong make syntax (pmackinn@redhat.com)

* Thu Nov 16 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-5
- Fixed wrong make syntax (pmackinn@redhat.com)

* Thu Nov 16 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-4
- Spec make build switched to accept release tag (pmackinn@redhat.com)

* Thu Nov 16 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-3
- Further make/build script fixes (pmackinn@redhat.com)

* Tue Nov 14 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-2
- Updates to spec and build script (pmackinn@redhat.com)

* Fri Nov 10 2017 Peter MacKinnon <pmackinn@redhat.com> v0.4.1-1
- New package built with tito
