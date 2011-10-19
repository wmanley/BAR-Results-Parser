import re
import sys
from result import *

class state_between_competitions:
	def __init__(self, stater):
		self.compname = ""
		self.stater = stater
	def do_line(self, line):
		m = re.match(r'(\d+) Entr(y|ies)', line)
		if m:
			entry_count = int(m.group(1))
			self.stater.entries_line_no = self.stater.lineno
			if entry_count == 1 and m.group(2) == "ies":
				sys.stderr.write('%s:%d:\n    Error: "1 Entry" should be used rather than "1 Entries" in competition "%s"\n' % (self.stater.filename, self.stater.lineno, self.compname))
			elif entry_count > 1 and m.group(2) == "y":
				sys.stderr.write('%s:%d:\n    Error: "%d Entries" should be used rather than "%d Entry" in competition "%s"\n' % (self.stater.filename, self.stater.lineno, entry_count, entry_count, self.compname))

			self.stater.enter_state_awaiting_header(self.compname, int(m.group(1)))
		elif line == "No Entries":
			self.stater.add_comp(competition(self.compname))
		else:
			self.compname = line.strip()
	def exit(self):
		return

class single:
	name = "single"
	header_regex = r'Position\s+Name\s+Score(\s+Medal)?'
	score_regex = r'\s*(\d+)(=?)\s+(\D*)\s+(-?\d+\.?\d*|No score)(\s+\d+x)?(\s+\(\d+\))?\s*(Bronze|Silver|Gold|Wine)?\s*$'

	def parse_score(self, score, nox):
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

	def build(self, m):
		nox = ""
		if m[5]:
			nox = m[5]
		return single_result(
			pos = int(m[0]),
			joint = (m[1] == "="),
			name = m[2].strip(),
			score = self.parse_score(m[3], nox),
			prize = m[6])

class manvman:
	name = "manvman"
	header_regex = r'Position\s+Name\s+Medal'
	score_regex = r'(\d+)(=?)\s+(\D*)'
	def build(self, m):
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

class aggregate:
	name = "aggregate"
	header_regex = r'Position\s+Name\s+Score\(stages 1/2/3/4/Tot\)\s+Medal'
	score_regex = r'(\d+)(=?)\s+(\D*)\s+((\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-))\s*\/\s*(\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
	
	def build(self, m):
		return aggregate_result(
			pos = int(m[0].strip()),
			joint = (m[1] == "="),
			name = m[2].strip(),
			scores = m[3].strip().split(" / "),
			score = std_score(int(m[8].strip())),
			prize = m[9].strip())

class timed(single):
	name = "timed"
	header_regex = r'Position\s+Name\s+Time\s+Medal'

class threeteam:
	name = "threeteam"
	header_regex = r'Position\s+Threesome\s+Score'
	score_regex = r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\),\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
	def build(self, m):
		return threeteam_result(
			pos = int(m[0]),
			joint = (m[1] == "="),
			competitors = [ (m[2].strip(), std_score(int(m[3]))),
					(m[4].strip(), std_score(int(m[5]))),
					(m[6].strip(), std_score(int(m[7])))],
			score = std_score(int(m[8])),
			prize = m[9].strip())

class twoteam:
	name = "twoteam"
	header_regex = r'Position\s+Pair\s+Score'
	score_regex = r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)(\s+\(Age \d+\))?((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
	def build(self, m):
		return twoteam_result(
			pos = int(m[0]),
			joint = (m[1] == "="),
			competitors = [ (m[2].strip(), std_score(int(m[3].strip()))),
					(m[4].strip(), std_score(int(m[5].strip())))],
			score = std_score(int(m[6])),
			prize = m[9])

# List used to match table headers to types of competition.
# Note: The order is important.  The regexps are evaluated in order and the
# first match is used.  Therefore it should go from most specific to most
# general 
headers = [single(), timed(), aggregate(), twoteam(), threeteam(), manvman()]

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
		for i in headers:
			if re.match(i.header_regex, line):
				ctype = i.name
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
		self.people = {}
	
	def do_line(self, line):
		if line == "":
			self.stater.enter_state_space()
		else:
			this_result = self.parse_result(line)
			pl = personlister()
			people = pl.get(this_result)
			for i in people:
				if i in self.people:
					print >>sys.stderr, self.stater.filename + ":" + str(self.stater.lineno) + ":"
					line_prefix = "    Error: "
					print >>sys.stderr, line_prefix + "\"" + i + "\" repeated in competition \"" + self.comp.name + "\""
					print >>sys.stderr, " "*len(line_prefix) + "Previously seen on line", str(self.people[i])
				self.people[i] = self.stater.lineno
			has_same_posn_as_previous = len(self.comp.results) > 0 and this_result.pos == self.comp.results[-1].pos
			previous_is_joint = len(self.comp.results) > 0 and self.comp.results[-1].joint
			expected_posn = len(self.comp.results) + 1
			if (this_result.pos == expected_posn) == (this_result.joint and previous_is_joint and has_same_posn_as_previous):
				if not has_same_posn_as_previous:
					sys.stderr.write('%s:%d:\n    Error: In competition "%s": "%s" should be in position %d, not %d\n' % (self.stater.filename, self.stater.lineno, self.comp.name, pl.get(this_result)[0], expected_posn, this_result.pos))
				else:
					sys.stderr.write('%s:%d:\n    Error: In competition "%s": "%s" shares position %d with "%s" but they are not both marked as joint\n' % (self.stater.filename, self.stater.lineno, self.comp.name, pl.get(this_result)[0], this_result.pos, pl.get(self.comp.results[-1])[0]))
			if len(self.comp.results) > 0 and self.comp.results[-1].joint and self.comp.results[-1].pos == len(self.comp.results) and not has_same_posn_as_previous:
				sys.stderr.write('%s:%d:\n    Error: In competition "%s" "%s" in position %d marked as joint but does not share a position with anybody\n' % (self.stater.filename, self.last_result_line_no, self.comp.name, pl.get(self.comp.results[-1])[0], this_result.pos))
			self.comp.results.append(this_result)
			self.last_result_line_no = self.stater.lineno

	def exit(self):
		if self.comp.entries != len(self.comp.results):
			sys.stderr.write('%s:%d:\n    Error: Competition "%s" has %d entries but claims to have %d\n' % (self.stater.filename, self.stater.entries_line_no, self.comp.name, len(self.comp.results), self.comp.entries))
		if len(self.comp.results) > 0:
			last = self.comp.results[-1]
			pl = personlister()
			people = pl.get(last)
			if last.joint and last.pos == len(self.comp.results):
				sys.stderr.write('%s:%d:\n    Error: In competition "%s" "%s" in position %d marked as joint but does not share a position with anybody\n' % (self.stater.filename, self.last_result_line_no, self.comp.name, pl.get(last)[0], last.pos))
		self.stater.add_comp(self.comp)
	
	def parse_result(self, line):
		for i in headers:
			match = re.match(i.score_regex, line)
			if match:
				return i.build(match.groups())
		
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
	
	def parse(self, instr, filename):
		self.filename = filename
		self.lineno = 0
		for line in instr:
			self.lineno = self.lineno + 1
			if self.nextstate:
				self.state.exit()
				self.state = self.nextstate
				self.nextstate = None
			self.state.do_line(line.strip())
		self.state.exit()
		return self.comps
	
	def enter_state_reading(self, cname, ctype, centries):
		self.nextstate = state_reading_scores(self, cname, ctype, centries)
	def enter_state_space(self):
		self.nextstate = state_between_competitions(self)
	def enter_state_awaiting_header(self, cname, ctype):
		self.nextstate = state_awaiting_header(self, cname, ctype)

