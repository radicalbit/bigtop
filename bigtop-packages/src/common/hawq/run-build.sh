#!/bin/bash

docker run --rm=true -v `pwd`:/data -u root rlei/mydocker:latest /bin/sh -c "date; \
cd /data/hawq-src/ ; \
./configure --prefix=/data/hawq ; \
if [ $? != 0 ]; then
    echo HAWQ configure failed.
    exit 1
fi
date; \
make -f Makefile.hawq-j8; \
if [ $? != 0 ]; then
    echo HAWQ compile failed.
    exit 1
fi
date; \
make -f Makefile.hawq install ; \
if [ $? != 0 ]; then
    echo HAWQ make install failed.
    exit 1
fi
date; \
"
