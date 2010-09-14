import re
import sys
from result import *

class state_between_competitions:
	def __init__(self, stater):
		self.compname = ""
		self.stater = stater
	def do_line(self, line):
		m = re.match(r'(\d+) Entries', line)
		if m:
			self.stater.enter_state_awaiting_header(self.compname, int(m.group(1)))
		elif line == "No Entries":
			self.stater.add_comp(competition(self.compname))
		else:
			self.compname = line.strip()
	def exit(self):
		return

def parse_score(score, nox):
	score = score.strip()
	s = 0
	x = 0
	if score:
		if score == "No score":
			return no_score()
		try:
			s = int(score)
		except ValueError:
			s = float(score)
	if nox:
		x = int(nox.strip("() \t"))
	return std_score(s, x)


def build_single(m):
	nox = ""
	if m[5]:
		nox = m[5]
	return single_result(
		pos = m[0],
		joint = (m[1] == "="),
		name = m[2].strip(),
		score = parse_score(m[3], nox),
		prize = m[6])

single = ("single",    r'Position\s+Name\s+Score(\s+Medal)?',
          r'\s*(\d+)(=?)\s+(\D*)\s+(-?\d+\.?\d*|No score)(\s+\d+x)?(\s+\(\d+\))?\s*(Bronze|Silver|Gold|Wine)?\s*$',
          build_single)

def build_manvman(m):
	p = re.match(r'(.+)(Bronze|Silver|Gold|Wine)\s*$', m[2].strip())
	if p:
		return manvman_result(
			pos = int(m[0].strip()),
			joint = (m[1] == "="),
			name = p.groups()[0].strip(),
			prize = p.groups()[1])
	else:
		return manvman_result(
			pos = int(m[0].strip()),
			joint = (m[1] == "="),
			name = m[2].strip(),
			prize = "")

manvman = ("manvman",   r'Position\s+Name\s+Medal',
           r'(\d+)(=?)\s+(\D*)', build_manvman)

def build_aggregate(m):
	return aggregate_result(
		pos = int(m[0].strip()),
		joint = (m[1] == "="),
		name = m[2].strip(),
		scores = m[3].strip().split(" / "),
		score = std_score(int(m[8].strip())),
		prize = m[9].strip())

aggregate = ("aggregate", r'Position\s+Name\s+Score\(stages 1/2/3/4/Tot\)\s+Medal',
             r'(\d+)(=?)\s+(\D*)\s+((\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-))\s*\/\s*(\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$',
             build_aggregate)

timed = ("timed",     r'Position\s+Name\s+Time\s+Medal',
         r'\s*(\d+)(=?)\s+(\D*)\s+(-?\d+\.?\d*|No score)(\s+\d+x)?(\s+\(\d+\))?\s*(Bronze|Silver|Gold|Wine)?\s*$',
         build_single)

def build_threeteam(m):
	return threeteam_result(
		pos = int(m[0]),
		joint = (m[1] == "="),
		competitors = [ (m[2].strip(), std_score(int(m[3]))),
				(m[4].strip(), std_score(int(m[5]))),
				(m[6].strip(), std_score(int(m[7])))],
		score = std_score(int(m[8])),
		prize = m[9].strip())

threeteam = ("threeteam", r'Position\s+Threesome\s+Score', 
             r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\),\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$',
             build_threeteam)

def build_twoteam(m):
	return twoteam_result(
		pos = int(m[0]),
		joint = (m[1] == "="),
		competitors = [ (m[2].strip(), std_score(int(m[3].strip()))),
				(m[4].strip(), std_score(int(m[5].strip())))],
		score = std_score(int(m[6])),
		prize = m[9])

twoteam = ("twoteam",   r'Position\s+Pair\s+Score', 
	r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)(\s+\(Age \d+\))?((\s+(Bronze|Silver|Gold|Wine))?)\s*$',
	build_twoteam)


# List used to match table headers to types of competition.
# Note: The order is important.  The regexps are evaluated in order and the
# first match is used.  Therefore it should go from most specific to most
# general 
headers = [single, timed, aggregate, twoteam, threeteam, manvman]

class state_awaiting_header:
	def __init__(self, stater, cname, centries):
		self.stater = stater
		self.parse_compname(cname)
		self.centries = centries
	
	def parse_compname(self, cname):
		cname = re.sub("\s\s+", " ", cname)
		m = re.match("(.*)\*", cname)
		if m:
			self.cname = m.group(1)
			self.exceptional = True
		else:
			self.cname = cname
			self.exceptional = False
	
	def do_line(self, line):
		""" Detect what type of table this is based on the header """
		ctype = ""
		for (name, head_regex, result_regex, result_fn) in headers:
			if re.match(head_regex, line):
				ctype = name
				break
		if ctype == "":
			print >> sys.stderr, "line ", self.stater.lineno, ": Expected table header.  Got '", line, "' instead!"
			self.stater.enter_state_space()
		self.stater.enter_state_reading(self.cname, ctype, self.centries)
	def exit(self):
		return

class state_reading_scores:
	def __init__(self, stater, cname, ctype, centries):
		self.stater = stater
		self.comp = competition(cname, ctype, centries)
	
	def do_line(self, line):
		if line == "":
			self.stater.enter_state_space()
		else:
			self.comp.results.append(self.parse_result(line))
	
	def exit(self):
		self.stater.add_comp(self.comp)
	
	def parse_result(self, line):
		for (name, head_regex, result_regex, result_fn) in headers:
			match = re.match(result_regex, line)
			if match:
				return result_fn(match.groups())
		
		print >>sys.stderr, "Line ", self.stater.lineno, ": Warning: unknown score format: '", line, "'"
		return bad_result(self.stater.lineno, line)

# State machine
class parser:
	def __init__(self):
		self.comps = []
		self.nextstate = None
		self.state = state_between_competitions(self)
	
	def add_comp(self, comp):
		self.comps.append(comp)
	
	def parse(self, instr):
		self.lineno = 0
		for line in instr:
			if self.nextstate:
				self.state.exit()
				self.state = self.nextstate
				self.nextstate = None
			self.lineno = self.lineno + 1
			self.state.do_line(line.strip())
		return self.comps
	
	def enter_state_reading(self, cname, ctype, centries):
		self.nextstate = state_reading_scores(self, cname, ctype, centries)
	def enter_state_space(self):
		self.nextstate = state_between_competitions(self)
	def enter_state_awaiting_header(self, cname, ctype):
		self.nextstate = state_awaiting_header(self, cname, ctype)

