#!/bin/bash

CWD=`pwd`
TESTS_PREFIX=$(dirname "$0")
export PREFIX=$(readlink -f "${TESTS_PREFIX}/..")

for i in ${TESTS_PREFIX}/*/*.test
do
    cd "$(dirname $i)"
    if "./$(basename $i)"
    then echo SUCCESS: $i
    else echo FAILURE: $i
    fi
    cd "$CWD"
done

