# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%define cassandra_name cassandra
%define lib_cassandra /usr/lib/%{cassandra_name}
%define bin_cassandra /usr/bin
%define var_run /var/run/cassandra
%define var_log /var/log/cassandra
%define var_lib /var/lib/cassandra
%define etc_cassandra /etc/%{cassandra_name}
%define config_cassandra %{etc_cassandra}/conf
%define man_dir %{_mandir}
%define _binaries_in_noarch_packages_terminate_build   0

%if  %{!?suse_version:1}0
%define doc_cassandra %{_docdir}/%{cassandra_name}
%define alternatives_cmd alternatives
%define build_cassandra %{_builddir}/%{cassandra_name}-%{cassandra_version}/

%else
%define doc_cassandra %{_docdir}/%{cassandra_name}
%define alternatives_cmd update-alternatives
%endif

Name: %{cassandra_name}
Version: %{cassandra_version}
Release: %{cassandra_release}
Summary: Apache cassandra
License: ASL 2.0
URL: http://cassandra.apache.org/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
BuildArch: noarch
Source0: cassandra-%{cassandra_base_version}.zip
Source1: do-component-build
Source2: install_cassandra.sh
Source3: bigtop.bom
#Requires: bigtop-utils >= 0.7

%description
Apache cassandra

%prep
%setup -n %{cassandra_name}-%{cassandra_base_version}

%build
bash $RPM_SOURCE_DIR/do-component-build
#env cassandra_VERSION=%{cassandra_base_version} bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT

bash %{SOURCE2} \
    --build-dir=%{build_cassandra} \
    --bin-dir=%{_bindir} \
    --var-dir=%{_var}  \
    --prefix="${RPM_BUILD_ROOT}"

#sh -x %{SOURCE2} --prefix=$RPM_BUILD_ROOT --doc-dir=%{doc_cassandra} --build-dir=%{build_cassandra}

%post
%{alternatives_cmd} --install %{config_cassandra} %{cassandra_name}-conf %{config_cassandra}.dist 30

%files
%defattr(-,root,root,755)
%config(noreplace) %{config_cassandra}.dist
%{lib_cassandra}
%{bin_cassandra}/cassandra
%{bin_cassandra}/cqlsh
%{bin_cassandra}/nodetool
%{var_run}
%{var_log}
%{var_lib}