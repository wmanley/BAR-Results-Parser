#!/bin/sh -e 

mkdir -p output/html_results_per_meeting/
cp depend/sorttable/sorttable.js output/html_results_per_meeting/

for i in results/fixedtxt/*.txt
do
    BASE=${i##*/}
    ./src/make_html.py "$i" "output/html_results_per_meeting/$BASE.html"
done

mkdir -p output/history_csv_per_person/
./src/make-time-csv.py results/fixedtxt/20*.txt

mkdir -p output/history_csv_per_comp/
./src/make-comp-time-csv.py results/fixedtxt/20*.txt

mkdir -p output/history_graph_per_comp/
cp depend/flot/* output/history_graph_per_comp/
./src/per-comp-stats.py results/fixedtxt/20*.txt

mkdir -p output/meeting_attendance_csv/
./src/meeting_stats.py results/fixedtxt/*.txt > output/meeting_attendance_csv/all.csv
./src/meeting_stats.py results/fixedtxt/*Autumn*.txt > output/meeting_attendance_csv/autumn.csv
./src/meeting_stats.py results/fixedtxt/*Spring*.txt > output/meeting_attendance_csv/spring.csv

