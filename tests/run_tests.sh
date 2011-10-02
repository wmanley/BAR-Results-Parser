#!/bin/bash

CWD=`pwd`
TESTS_PREFIX=$(dirname "$0")

for i in ${TESTS_PREFIX}/*/*.test
do
    cd "$(dirname $i)"
    if "./$(basename $i)" > "$CWD"/output.txt
    then echo SUCCESS: $i
    else echo FAILURE: $i
    fi
    cd "$CWD"
done

