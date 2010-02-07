#!/usr/bin/python

import parser
import result
import sys
import abbreviation

class personAggregator:
	def __init__(self):
		self.people = {}
	
	def add_results(self, results, meeting):
		self.meeting = meeting
		for comp in results:
			self.cname = comp.name
			for res in comp.results:
				self.add_result(res)
	
	def add_result(self, res):
		p = result.personlister()
		for i in p.get(res):
			if i not in self.people:
				self.people[i] = []
			self.people[i].append( (self.meeting, self.cname, res) )

def load(filenames):
	agg = personAggregator()
	meetings = []
	for filename in filenames:
		print >>sys.stderr, "Loading", filename
		p=parser.parser()
		f = file(filename, "r")
		res = p.parse(f)
		f.close()
		amapper = abbreviation.mapper()
		for i in res:
			for k in i.results:
				amapper.analyse_result(k)
		remapper = abbreviation.remapper(amapper.shorts)
		for i in res:
			for k in i.results:
				remapper.fix_result(k)
		agg.add_results(res, filename)
		meetings.append(filename)
	return (meetings, agg.people)

def output(meetings, people):
	s = score_getter()
	meetings.sort()
	for name,entries in people.iteritems():
		f = file("out/" + name + ".csv", "w")
		entries.sort(lambda a, b: cmp(a[1], b[1]) or cmp(a[0], b[0]))
		for m in meetings:
			f.write("," + m)
		comp = ""
		mpos = 0
		for e in entries:
			if comp != e[1]:
				mpos = 0
				comp = e[1]
				f.write("\n" + comp + ",")
			
			while meetings[mpos] != e[0]:
				mpos = mpos + 1
				f.write(",")
			f.write(str(s.get(e[2])))
		f.close()

(m, p) = load(sys.argv[1:])
output(m, p)

