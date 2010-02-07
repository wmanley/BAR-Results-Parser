#!/bin/bash

mkdir -p output/html_results_per_meeting/
cp depend/sorttable/sorttable.js output/html_results_per_meeting/
find results/fixedtxt/ -name \*.txt -print0 | xargs -0 -n1 ./src/make_html.py

mkdir output/history_csv_per_person/
./src/make-time-csv.py results/fixedtxt/20*.txt

mkdir output/history_graph_per_comp/
cp depend/flot/* output/history_graph_per_comp/
./src/per-comp-stats.py results/fixedtxt/20*.txt


