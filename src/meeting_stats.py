#!/usr/bin/python

import parser
import result
import sys
import abbreviation
import re

bins=[0, 2, 5, 10, 20, 40]

class competitionAnalysis:
	def __init__(self):
		self.appearances = 0
		self.entries = {}
	
	def add_result(self, res):
		p = result.personlister()
		people = p.get(res)
		for person in people:
			if not person in self.entries.keys():
				self.entries[person] = 0
			self.entries[person] = self.entries[person] + 1
	
	def get_bin_data(self):
		outbin = [0] * len(bins)
		for (n, p) in self.entries.items():
			for i in range(0, len(bins)):
				if p > bins[i]:
					outbin[i]=outbin[i]+1
		return outbin

class competitionAggregator:
	def __init__(self):
		self.meets = []
	
	def add_results(self, results, date):
		c=competitionAnalysis()
		for comp in results:
			for res in comp.results:
				c.add_result(res)
		self.meets.append( (date, c.get_bin_data() ) )
	
	def print_bin_data(self, out):
		for i in self.meets:
			out.write(str(i[0]))
			for j in i[1]:
				out.write(","+str(j))
			out.write("\n")

def load(filenames):
	agg = competitionAggregator()
	meetings = []
	for filename in filenames:
		p=parser.parser()
		f = file(filename, "r")
		res = p.parse(f, filename)
		f.close()
		m = re.search("(\d+)-(\d+)", filename)
		date = float(m.groups(1)[0]) + float(m.groups(1)[1])/12
		
		amapper = abbreviation.mapper()
		for i in res:
			for k in i.results:
				amapper.analyse_result(k)
		remapper = abbreviation.remapper(amapper.shorts)
		for i in res:
			for k in i.results:
				remapper.fix_result(k)
		
		agg.add_results(res, date)
		meetings.append(filename)
	return agg

sys.stdout.write("Meeting")
for i in bins:
	sys.stdout.write(",>" + str(i) + " Entries")
sys.stdout.write("\n")

p = load(sys.argv[1:]).print_bin_data(sys.stdout)
#output(p)
#output_flot_graph(p, sys.stdout)
