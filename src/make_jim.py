#!/usr/bin/python

import parser
import jim_printer
import jim_html_printer
import sys
import abbreviation
import person
import re
import os
from optparse import OptionParser

prefix = os.environ["PREFIX"] if "PREFIX" in os.environ else "."

def make_jim(instream, printer, title):
	p = parser.parser()

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

def main(argv):
	op = OptionParser()
	op.add_option("-f", "--format", dest="format", choices=["txt", "html"], default="txt")
	(options, (input_filename, output_filename)) = op.parse_args(argv[1:])

	title = re.sub(".txt$", "", input_filename)
	title = re.sub("^.*/", "", title)
	outfile = file(output_filename, "w")
	infile = file(input_filename, "r")

	if options.format == "html":
		printer = jim_html_printer.printer(outfile)
	elif options.format == "txt":
		printer = jim_printer.printer(outfile)
	else:
		assert False
	make_jim(infile, printer, title)

sys.exit(main(sys.argv))

