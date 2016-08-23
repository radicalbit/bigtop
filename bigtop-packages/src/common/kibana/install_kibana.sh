#!/bin/bash

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

set -ex

usage() {
  echo "
usage: $0 <options>
  Required not-so-options:
     --build-dir=DIR             path to kibana dist.dir
     --prefix=PREFIX             path to install into

  Optional options:
     --bin-dir=DIR               path to install bin
     ... [ see source for more similar options ]
  "
  exit 1
}

OPTS=$(getopt \
  -n $0 \
  -o '' \
  -l 'prefix:' \
  -l 'bin-dir:' \
  -l 'var-dir:' \
  -l 'lib-dir:' \
  -l 'build-dir:' -- "$@")

if [ $? != 0 ] ; then
    usage
fi

eval set -- "$OPTS"
while true ; do
    case "$1" in
        --prefix)
        PREFIX=$2 ; shift 2
        ;;
        --build-dir)
        BUILD_DIR=$2 ; shift 2
        ;;
        --lib-dir)
        LIB_DIR=$2 ; shift 2
        ;;
        --bin-dir)
        BIN_DIR=$2 ; shift 2
        ;;
        --var-dir)
        VAR_DIR=$2 ; shift 2
        ;;
        --)
        shift ; break
        ;;
        *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
done

for var in PREFIX BUILD_DIR ; do
  if [ -z "$(eval "echo \$$var")" ]; then
    echo Missing param: $var
    usage
  fi
done

LIB_DIR=${LIB_DIR:-/usr/lib/kibana}
BIN_DIR=${BIN_DIR:-/usr/bin}
CONF_DIR=${CONF_DIR:-/etc/kibana/conf.dist}

install -d -m 0755 $PREFIX/$LIB_DIR
install -d -m 0755 $PREFIX/$LIB_DIR/bin
install -d -m 0755 $PREFIX/$LIB_DIR/installedPlugins
install -d -m 0755 $PREFIX/$LIB_DIR/node_modules
install -d -m 0755 $PREFIX/$LIB_DIR/optimize
install -d -m 0755 $PREFIX/$LIB_DIR/src
install -d -m 0755 $PREFIX/$LIB_DIR/webpackShims
install -d -m 0755 $PREFIX/etc
install -d -m 0755 $PREFIX/etc/kibana
install -d -m 0755 $PREFIX/etc/kibana/conf
install -d -m 0755 $PREFIX/$VAR_DIR/log/kibana
install -d -m 0755 $PREFIX/$VAR_DIR/lib/kibana
install -d -m 0755 $PREFIX/$VAR_DIR/run/kibana

cp -a bin/* $PREFIX/${LIB_DIR}/bin
rm -f $PREFIX/${LIB_DIR}/bin/*.bat
cp -a installedPlugins/* $PREFIX/${LIB_DIR}/installedPlugins
cp -a node_modules/* $PREFIX/${LIB_DIR}/node_modules
cp -a optimize/* $PREFIX/${LIB_DIR}/optimize
cp -a src/* $PREFIX/${LIB_DIR}/src
cp -a webpackShims/* $PREFIX/${LIB_DIR}/webpackShims

# Copy in the configuration files
install -d -m 0755 $PREFIX/$CONF_DIR
cp -a ${BUILD_DIR}/conf/* $PREFIX/$CONF_DIR
ln -s /etc/kibana/conf $PREFIX/$LIB_DIR/conf

# Copy in the /usr/bin/kibana wrapper
install -d -m 0755 $PREFIX/$BIN_DIR

# Prefix is correct at time of install,
# but we dont want to escape it before that point.
cat > $PREFIX/$BIN_DIR/kibana <<EOF
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome
# Lib dir => ${LIB_DIR}
#!/usr/bin/env bash
exec ${LIB_DIR}/bin/kibana "\$@"
EOF
chmod 755 $PREFIX/$BIN_DIR/kibana
