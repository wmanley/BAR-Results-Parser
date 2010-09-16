#!/usr/bin/python

import parser
import html_printer
import sys
import abbreviation
import person
import re
import os

prefix = os.environ["PREFIX"] if "PREFIX" in os.environ else "."

def make_html(instream, outstream, title):
	p = parser.parser()
	printer = html_printer.printer(outstream)

	print >>outstream, "<html><head><title>", title, " - British Alpine Rifles</title>"
	head = file(prefix + "/header.html")
	for i in head:
		print >>outstream, i
	print >>outstream, "<h1>", title, " - British Alpine Rifles</h1>"
	print >>outstream, "<p>Click on a name to have all instances of that name highlighted.</p>"

	j = p.parse(instream, sys.argv[1])

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
		print >>outstream, "\n"

	print >>outstream, "<h1>Per-person summary</h1>\n<p>Note: you can click the table headings for different sortings</p>"
	pp = html_printer.personlist_printer(peo.people.values(), True, outstream)
	pp.print_people()

if len(sys.argv) != 3:
	print >>sys.stderr, "Usage ", sys.argv[0], " input-file output-file"
	sys.exit(1)

title = re.sub(".txt$", "", sys.argv[1])
title = re.sub("^.*/", "", title)
outfile = file(sys.argv[2], "w")
infile = file(sys.argv[1], "r")
make_html(infile, outfile, title)
