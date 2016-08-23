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
%define        kibana_name kibana
%define        kibana_home /usr/lib/%{kibana_name}
%define        kibana_bin /usr/bin
%define        var_lib /var/lib/%{kibana_name}
%define        var_run /var/run/%{kibana_name}
%define        var_log /var/log/%{kibana_name}
%define        etc_kibana /etc/%{kibana_name}
%define        config_kibana %{etc_kibana}/conf

#%global        initd_dir %{_sysconfdir}/init.d
%define        alternatives_cmd update-alternatives

%define build_kibana %{_builddir}/%{kibana_name}-%{kibana_version}/build/kibana/

#%if  %{?suse_version:1}0
## Required for init scripts
#Requires: insserv
#%global        initd_dir %{_sysconfdir}/rc.d
#
#%else
## Required for init scripts
#Requires: /lib/lsb/init-functions
#
#%global        initd_dir %{_sysconfdir}/rc.d/init.d
#
#%endif
%global        initd_dir /usr/rbp/kibana

# disable repacking jars
%define __arch_install_post %{nil}

Name:           kibana
Version:        %{kibana_version}
Release:        %{kibana_release}
Summary:       Kibana is an open source data visualization platform that allows you to interact with your data through stunning, powerful graphics
License:       ASL 2.0
URL:           https://www.elastic.co/products/kibana/
Group:         Development/Libraries
BuildArch:     noarch

Source0:       %{kibana_name}-%{kibana_base_version}.zip
Source1:       do-component-build
Source2:       install_kibana.sh
Source3:       init.d.tmpl
# #BIGTOP_PATCH_FILES
Requires: bigtop-utils

%description
Kibana is an open source data visualization platform that allows you to
interact with your data through stunning, powerful graphics.
From histograms to geomaps, Kibana brings your data to life with visuals
that can be combined into custom dashboards that help you share insights
from your data far and wide.

%prep
%setup -n %{kibana_name}-%{kibana_base_version}

# #BIGTOP_PATCH_COMMANDS

%build
bash $RPM_SOURCE_DIR/do-component-build

%install
rm -rf $RPM_BUILD_ROOT

# See /usr/lib/rpm/macros for info on how vars are defined.
# Here we run the kibana installation script.
bash %{SOURCE2} \
    --build-dir=%{build_kibana} \
    --bin-dir=%{_bindir} \
    --var-dir=%{_var}  \
    --prefix="${RPM_BUILD_ROOT}"

%post
%{alternatives_cmd} --install %{config_kibana} %{kibana_name}-conf %{config_kibana}.dist 30

%preun
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{kibana_name}-conf %{config_kibana}.dist || :
fi

%files
%defattr(-,root,root,755)
%config(noreplace) %{config_kibana}.dist
%{kibana_home}
%{kibana_bin}/kibana
%attr(0755,root,root) %{var_lib}
%attr(0755,root,root) %{var_run}
%attr(0755,root,root) %{var_log}

%clean
rm -rf $RPM_BUILD_ROOT
