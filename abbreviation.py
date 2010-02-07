import re
import sys
import result

class mapper:
	def __init__(self):
		self.shorts = {}
	
	def shortern_name(self, name):
		m = re.match(r'(\w)[\w-]*\s+(\S.*)', name)
		if m:
			return m.groups()[0] + " " + m.groups()[1]
		else:
			print >>sys.stderr, "Warning: could not parse name '" + name + "'"
			return name
	
	def analyse_result(self, res):
		p = result.personlister()
		for i in p.get(res):
			self.add_name(i)
	
	def add_name(self, name):
		s = self.shortern_name(name)
		if s == name:
			return
		if s in self.shorts:
			if name not in self.shorts[s]:
				self.shorts[s].append(name)
				print >>sys.stderr, "Warning: Duplicate abbreviation '", s, "' for ", self.shorts[s]

		else:
			self.shorts[s] = [name]

class remapper:
	def __init__(self, shorts):
		self.shorts = shorts
	
	def fix_name(self, name):
		if name in self.shorts:
			if len(self.shorts[name]) == 1:
				return self.shorts[name][0]
			else:
				print >>sys.stderr, "Error: Ambiguous match: ", name, " for ", self.shorts[name]
		elif re.match("\w\s.*", name):
			self.shorts[name] = [self.find_exceptional_name(name)]
			return self.shorts[name][0]
		else:
			return name
	
	def find_exceptional_name(self, name):
		print >>sys.stderr, "Could not find abbreviation ", name
		m = re.match(r'(\w)\w*\s+(\S.*)', name)
		r = re.compile(r'\w+\s+' + m.groups()[1])
		matches = [j for i in self.shorts.values() for j in i if r.match(j)]
		if len(matches) == 0:
			print >>sys.stderr, "\tSearch failed!", name
			return name
		elif len(matches) == 1:
			print >>sys.stderr, "\tMatched: ", matches[0]
			return matches[0]
		else:
			print >>sys.stderr, "\tError: Ambiguous match:", matches
			return name
	
	def fix_result(self, result):
		result.visit(self)
	
	def fix_team(self, res):
		x=0
		for i in res.competitors:
			res.competitors[x] = (self.fix_name(i[0]), i[1])
			x=x+1	
	
	def visit_threeteam(self, res):
		self.fix_team(res)
		
	def visit_twoteam(self, res):
		self.fix_team(res)
	
	def visit_aggregate(self, res):
		res.name = self.fix_name(res.name)
	
	def visit_single(self, res):
		res.name = self.fix_name(res.name)
			
	def visit_manvman(self, res):
		res.name = self.fix_name(res.name)

