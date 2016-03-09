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

set -e

usage() {
  echo "
usage: $0 <options>
  Required not-so-options:
     --build-dir=DIR             path to flink dist.dir
     --prefix=PREFIX             path to install into
  Optional options:
     --lib-dir=DIR               path to install flink home [/usr/lib/cassandra]
     --bin-dir=DIR               path to install bins [/usr/bin]
     ... [ see source for more similar options ]
  "
  exit 1
}

OPTS=$(getopt \
  -n $0 \
  -o '' \
  -l 'prefix:' \
  -l 'var-dir:' \
  -l 'lib-dir:' \
  -l 'bin-dir:' \
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

LIB_DIR=${LIB_DIR:-/usr/lib/cassandra}
BIN_DIR=${BIN_DIR:-/usr/bin}
CONF_DIR=${CONF_DIR:-/etc/cassandra/conf.dist}

install -d -m 0755 $PREFIX/$LIB_DIR
install -d -m 0755 $PREFIX/$LIB_DIR/bin
install -d -m 0755 $PREFIX/$LIB_DIR/lib
install -d -m 0755 $PREFIX/$LIB_DIR/build
install -d -m 0755 $PREFIX/$LIB_DIR/pylib
install -d -m 0755 $PREFIX/$VAR_DIR/lib/cassandra
install -d -m 0755 $PREFIX/$VAR_DIR/log/cassandra
install -d -m 0755 $PREFIX/$VAR_DIR/run/cassandra

cp -ra ${BUILD_DIR}/lib/* $PREFIX/${LIB_DIR}/lib/
cp -a ${BUILD_DIR}/bin/* $PREFIX/${LIB_DIR}/bin
cp -ra ${BUILD_DIR}/build/* $PREFIX/${LIB_DIR}/build/
cp -ra ${BUILD_DIR}/pylib/* $PREFIX/${LIB_DIR}/pylib/

rm -rf $PREFIX/${LIB_DIR}/bin/*.bat
rm -rf $PREFIX/${LIB_DIR}/lib/sigar-bin/*.dll
rm -rf $PREFIX/${LIB_DIR}/lib/sigar-bin/*.lib

# Copy in the configuration files
install -d -m 0755 $PREFIX/$CONF_DIR
cp -a ${BUILD_DIR}/conf/* $PREFIX/$CONF_DIR
ln -s /etc/flink/conf $PREFIX/$LIB_DIR/conf

# Copy in the /usr/bin/flink wrapper
install -d -m 0755 $PREFIX/$BIN_DIR
cat > $PREFIX/$BIN_DIR/cassandra <<EOF

!/bin/bash
# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

EOF
chmod 755 $PREFIX/$BIN_DIR/cassandra