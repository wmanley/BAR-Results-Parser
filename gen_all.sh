#!/bin/bash
find results/fixedtxt/ -name \*.txt -print0 | xargs -0 -n1 ./make_html.py
