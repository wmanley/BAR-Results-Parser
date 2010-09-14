#!/bin/bash

CWD=`pwd`

for i in */*.test
do
    cd "$(dirname $i)"
    if "./$(basename $i)" > "$CWD"/output.txt
    then echo SUCCESS: $i
    else echo FAILURE: $i
    fi
    cd "$CWD"
done

