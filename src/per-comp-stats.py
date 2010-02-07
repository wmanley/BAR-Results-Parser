#!/usr/bin/python

import parser
import result
import sys
import abbreviation
import re

class competitionAnalysis:
	def __init__(self):
		self.appearances = 0
		self.people = {}
	
	def add_result(self, date, res):
		p = result.personlister()
		people = p.get(res)
		s = result.score_getter()
		ss = result.score_valuer()
		score = ss.get(s.get(res))
		for person in people:
			if not person in self.people.keys():
				self.people[person] = []
			self.people[person].append( (date, score) )
	
	def print_flot_data(self, out):
		items = self.people.items()
		items.sort()
		for (n, d) in items:
			if len(d) < 2:
				continue
			out.write("\"" + n + "\": {")
			out.write("label: \"" + n + "\",")
			out.write("data: [")
			for i in d:
				out.write("[" + str(i[0]) + ", " + str(i[1]) + "], ")
			out.write("]},")

class competitionAggregator:
	def __init__(self):
		self.comps = {}
	
	def add_results(self, results, date):
		self.meeting = date
		for comp in results:
			if not comp.name in self.comps:
				self.comps[comp.name] = competitionAnalysis()
			self.comps[comp.name].appearances = self.comps[comp.name].appearances + 1
			for res in comp.results:
				self.comps[comp.name].add_result(date, res)

def load(filenames):
	agg = competitionAggregator()
	meetings = []
	for filename in filenames:
		p=parser.parser()
		f = file(filename, "r")
		res = p.parse(f)
		f.close()
		m = re.search("(\d+)-(\d+)", filename)
		date = float(m.groups(1)[0]) + float(m.groups(1)[1])/12
		agg.add_results(res, date)
		meetings.append(filename)
	return agg.comps

def output_appearences(comps):
	for name,entries in comps.iteritems():
		print name, ":\t ", entries.appearances

def read_file(filename):
	f = file(filename, "r")
	txt = ""
	for line in f:
		txt = txt + line
	f.close()
	return txt

def output_flot_graph(comps, out):
	header = read_file("flot_header.html")
	footer = read_file("flot_footer.html")
	for (name,comp) in comps.iteritems():
		f = file("output/history_graph_per_comp/"+name+".html", "w")
		f.write(header)
		comp.print_flot_data(f)
		f.write(footer)
		f.close()

p = load(sys.argv[1:])
#output(p)
output_flot_graph(p, sys.stdout)
