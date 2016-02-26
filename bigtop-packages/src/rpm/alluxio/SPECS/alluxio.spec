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
%define        alluxio_name alluxio
%define        alluxio_home /usr/lib/%{alluxio_name}
%define        alluxio_services master worker
%define        var_lib /var/lib/%{alluxio_name}
%define        var_run /var/run/%{alluxio_name}
%define        var_log /var/log/%{alluxio_name}
%define        etc_alluxio /etc/%{alluxio_name}
%define        config_alluxio %{etc_alluxio}/conf

%global        initd_dir %{_sysconfdir}/init.d
%define        alternatives_cmd update-alternatives

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

# disable repacking jars
%define __arch_install_post %{nil}

Name:           alluxio
Version:        %{alluxio_version}
Release:        %{alluxio_release}
Summary:       Reliable file sharing at memory speed across cluster frameworks
License:       ASL 2.0
URL:           http://alluxio.org/
Group:         Development/Libraries
BuildArch:     noarch

Source0:       %{alluxio_name}-%{alluxio_base_version}-bin.tar.gz
Source1:       do-component-build
Source2:       install_alluxio.sh
Source3:       init.d.tmpl
Source4:       alluxio-master.svc
Source5:       alluxio-worker.svc
#BIGTOP_PATCH_FILES
Requires: bigtop-utils

%description
Alluxio is a fault tolerant distributed file system
enabling reliable file sharing at memory-speed
across cluster frameworks, such as Spark and MapReduce.
It achieves high performance by leveraging lineage
information and using memory aggressively.
Alluxio caches working set files in memory, and
enables different jobs/queries and frameworks to
access cached files at memory speed. Thus, Alluxio
avoids going to disk to load data-sets that
are frequently read.

%package master
Summary: Master node for alluxio
Group: System/Daemons
Requires: alluxio = %{alluxio_version}-%{alluxio_release}

%description master
Bundles the init script for Alluxio master node.

%package worker
Summary: Worker node for alluxio
Group: System/Daemons
Requires: alluxio = %{alluxio_version}-%{alluxio_release}

%description worker
Bundles the init script for Alluxio worker node.

%prep
%setup -n %{alluxio_name}-%{alluxio_base_version}

#BIGTOP_PATCH_COMMANDS

%build
bash $RPM_SOURCE_DIR/do-component-build

%install
rm -rf $RPM_BUILD_ROOT

# See /usr/lib/rpm/macros for info on how vars are defined.
# Here we run the alluxio installation script.
bash %{SOURCE2} \
    --build-dir=%{buildroot} \
    --bin-dir=%{_bindir} \
    --data-dir=%{_datadir} \
    --libexec-dir=%{_libexecdir} \
    --var-dir=%{_var}  \
    --prefix="${RPM_BUILD_ROOT}"

for service in %{alluxio_services}
do
    # Install init script
    init_file=$RPM_BUILD_ROOT/%{initd_dir}/%{alluxio_name}-${service}
    bash $RPM_SOURCE_DIR/init.d.tmpl $RPM_SOURCE_DIR/alluxio-${service}.svc rpm $init_file
done

#%preun
#for service in %{alluxio_services}; do
#  /sbin/service %{alluxio_name}-${service} status > /dev/null 2>&1
#  if [ $? -eq 0 ]; then
#    /sbin/service %{alluxio_name}-${service} stop > /dev/null 2>&1
#  fi
#done

##############################
#### Alluxio core section ####
##############################
%post
%{alternatives_cmd} --install %{config_alluxio} %{alluxio_name}-conf %{config_alluxio}.dist 30

%preun
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{alluxio_name}-conf %{config_alluxio}.dist || :
fi

for service in %{alluxio_services}; do
  /sbin/service %{alluxio_name}-${service} status > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    /sbin/service %{alluxio_name}-${service} stop > /dev/null 2>&1
  fi
done

################################
#### Alluxio master section ####
################################
%post master
chkconfig --add %{alluxio_name}-master

%preun master
/sbin/service %{alluxio_name}-master status > /dev/null 2>&1
if [ $? -eq 0  ] ; then
  service %{alluxio_name}-master stop > /dev/null 2>&1
  chkconfig --del %{alluxio_name}-master
fi

%postun master
if [ $1 -ge 1 ]; then
  service %{alluxio_name}-master condrestart >/dev/null 2>&1
fi

################################
#### Alluxio worker section ####
################################
%post worker
chkconfig --add %{alluxio_name}-worker

%preun worker
/sbin/service %{alluxio_name}-worker status > /dev/null 2>&1
if [ $? -eq 0  ] ; then
  service %{alluxio_name}-worker stop > /dev/null 2>&1
  chkconfig --del %{alluxio_name}-worker
fi

%postun worker
if [ $1 -ge 1 ]; then
  service %{alluxio_name}-worker condrestart >/dev/null 2>&1
fi

#######################
#### FILES SECTION ####
#######################
%files master
%attr(0755,root,root) %{initd_dir}/%{alluxio_name}-master

%files worker
%attr(0755,root,root) %{initd_dir}/%{alluxio_name}-worker

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%dir %{_sysconfdir}/%{alluxio_name}
%config(noreplace) %{_sysconfdir}/%{alluxio_name}/conf/log4j.properties
%config(noreplace) %{_sysconfdir}/%{alluxio_name}/conf/workers
#%config(noreplace) %{initd_dir}/%{alluxio_name}-master
#%config(noreplace) %{initd_dir}/%{alluxio_name}-worker
%config(noreplace) %{_sysconfdir}/%{alluxio_name}/conf/alluxio-env.sh
%config(noreplace) %{alluxio_home}/libexec/alluxio-layout.sh
%attr(0755,root,root) %{var_lib}
%attr(0755,root,root) %{var_run}
%attr(0755,root,root) %{var_log}
%{alluxio_home}/alluxio*
%{alluxio_home}/bin/alluxio*
%{alluxio_home}/libexec/alluxio*
%{_datadir}/%{alluxio_name}
/usr/bin/alluxio
%{alluxio_home}/share


%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Tue Feb 23 2016 Mauro Cortellazzi
- upgrade to Alluxio 1.0.0
