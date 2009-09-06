#!/usr/bin/python

import parser
import jim_printer
import sys

p = parser.parser()
printer = jim_printer.printer(sys.stdout)

m = file(sys.argv[1], "r")
j = p.parse(m)
for i in j:
    printer.print_comp(i)
    print "\n"


