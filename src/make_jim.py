#!/usr/bin/python

import parser
import jim_printer
import sys
import abbreviation
import person
import re
import os

prefix = os.environ["PREFIX"] if "PREFIX" in os.environ else "."

def make_jim(instream, outstream, title):
	p = parser.parser()
	printer = jim_printer.printer(outstream)

	j = p.parse(instream, sys.argv[1])

	amapper = abbreviation.mapper()
	for i in j:
		for k in i.results:
			amapper.analyse_result(k)

	remapper = abbreviation.remapper(amapper.shorts)

	for i in j:
		for k in i.results:
			remapper.fix_result(k)

	for i in j:
		printer.print_comp(i)
		print >>outstream, "\n"

def main(argv):
	if len(argv) != 3:
		print >>sys.stderr, "Usage ", argv[0], " input-file output-file"
		return 1

	(input_filename, output_filename) = argv[1:]

	title = re.sub(".txt$", "", input_filename)
	title = re.sub("^.*/", "", title)
	outfile = file(output_filename, "w")
	infile = file(input_filename, "r")
	make_jim(infile, outfile, title)

sys.exit(main(sys.argv))

