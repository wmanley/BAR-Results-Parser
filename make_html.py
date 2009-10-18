#!/usr/bin/python

import parser
import html_printer
import sys
import abbreviation
import person

p = parser.parser()
printer = html_printer.printer(sys.stdout)

head = file("header.html")
for i in head:
	print i

m = file(sys.argv[1], "r")
j = p.parse(m)

amapper = abbreviation.mapper()
for i in j:
	for k in i.results:
		amapper.analyse_result(k)

remapper = abbreviation.remapper(amapper.shorts)
peo = person.analyser()
for i in j:
	for k in i.results:
		remapper.fix_result(k)
		peo.analyse_result(k)

for i in j:
	printer.print_comp(i)
	print "\n"

print "<h1>Per-person summary</h1>\n<p>Note: you can click the table headings for different sortings</p>"
pp = html_printer.personlist_printer(peo.people.values(), True)
pp.print_people()
