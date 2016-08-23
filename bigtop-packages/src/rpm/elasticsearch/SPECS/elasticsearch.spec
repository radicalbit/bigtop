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

%define elasticsearch_name elasticsearch
%define lib_elasticsearch /usr/lib/%{elasticsearch_name}
%define bin_elasticsearch /usr/bin
%define etc_elasticsearch /etc/%{elasticsearch_name}
%define config_elasticsearch %{etc_elasticsearch}/conf
%define man_dir %{_mandir}
%define var_lib /var/lib/%{elasticsearch_name}
%define var_run /var/run/%{elasticsearch_name}
%define var_log /var/log/%{elasticsearch_name}

%if  %{!?suse_version:1}0
%define alternatives_cmd alternatives
%define build_elasticsearch %{_builddir}/%{elasticsearch_name}-%{elasticsearch_version}/distribution/rpm/target/
%define conf_elasticsearch %{_builddir}/%{elasticsearch_name}-%{elasticsearch_version}/distribution/src/main/resources/config/

%else
%define alternatives_cmd update-alternatives
%endif

Name: %{elasticsearch_name}
Version: %{elasticsearch_version}
Release: %{elasticsearch_release}
Summary: Elasticsearch is a distributed, open source search and analytics engine, designed for horizontal scalability, reliability, and easy management.
License: ASL 2.0
URL: https://www.elastic.co/products/elasticsearch
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
BuildArch: noarch
Source0: elasticsearch-%{elasticsearch_base_version}.tar.gz
Source1: do-component-build
Source2: install_elasticsearch.sh
Source3: bigtop.bom
Requires: bigtop-utils >= 0.7

%description
Elasticsearch is a distributed, open source search and analytics engine,
designed for horizontal scalability, reliability, and easy management.
It combines the speed of search with the power of analytics via a sophisticated,
developer-friendly query language covering structured, unstructured,
and time-series data.

%prep
%setup -n %{name}-%{elasticsearch_base_version}

%build
bash $RPM_SOURCE_DIR/do-component-build
#env elasticsearch_VERSION=%{elasticsearch_base_version} bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT

sh -x %{SOURCE2} --prefix=$RPM_BUILD_ROOT --build-dir=%{build_elasticsearch} --source-conf-dir=%{conf_elasticsearch}

%post
%{alternatives_cmd} --install %{config_elasticsearch} %{elasticsearch_name}-conf %{config_elasticsearch}.dist 30

%files
%defattr(-,root,root,755)
%config(noreplace) %{config_elasticsearch}.dist
%{lib_elasticsearch}
%{bin_elasticsearch}/elasticsearch
%attr(0755,root,root) %{var_lib}
%attr(0755,root,root) %{var_run}
%attr(0755,root,root) %{var_log}
