#!/usr/bin/python

import re
import sys
from result import *

class parser:
	lineno = 0
	def parse(self, instr):
		comps = []
		comp = competition()
		lineno = 0
		state = "between competitions"
		
		for line in instr:
			lineno = lineno + 1
			oldstate = state;
		
			if state == "reading scores":
				if re.match(r'\s+', line):
					comps.append(comp)
					
					state = "between competitions"
					comp = competition()
				else:
					comp.results.append(self.parse_result(line))
			elif state == "between competitions":
				m = re.match(r'\s*(\d+) Entries\s*', line)
				if m:
					comp.entries = int(m.group(1))
					state = "awaiting header";
				elif re.match(r'\s*No Entries\s*', line):
					comp.entries = 0
					comps.append(comp)
				else:
					comp.name = line.strip()
			elif state == "awaiting header":
				if re.search(r'\t', line):
					state = "reading scores"
					if re.match(r'Position\s+Name\s+Score\s+Medal', line):
						comp.type="single"
					if re.match(r'Position\s+Name\s+Medal', line):
						comp.type="manvman"
					elif re.match(r'Position\s+Name\s+Time\s+Medal', line):
						comp.type="timed"
					elif re.match(r'Position\s+Threesome\s+Score', line):
						comp.type="threeteam"
					elif re.match(r'Position\s+Pair\s+Score', line):
						comp.type="twoteam"
					elif re.match(r'Position\s+Name\s+Score\(stages 1/2/3/4/Tot\)\s+Medal', line):
						comp.type="aggregate"	
				else:
					print >> sys.stderr, "line ", lineno, ": Expected table header.  Got '", line, "' instead!"
					state = "between competitions"
			else:
				print >> STDERR,  "line ", lineno, ": unexpected state '", state, "'"
		return comps
	
	def parse_result(self, line):
		match_single = re.match(r'\s*(\d+)(=?)\s+(\D*)\s+(-?\d+\.?\d*|No score)(\s+\d+x)?(\s+\(\d+\))?\s*(Bronze|Silver|Gold)?\s*$', line)
		match_agg = re.match(r'(\d+)(=?)\s+(\D*)\s+((\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-))\s*\/\s*(\d+)((\s+(Bronze|Silver|Gold))?)', line)
		match_twoteam  = re.match(r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)(\s+\(Age \d+\))?((\s+(Bronze|Silver|Gold))?)', line)
		match_threeteam = re.match(r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\),\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)((\s+(Bronze|Silver|Gold))?)', line)
		match_manvman = re.match(r'(\d+)(=?)\s+(\D*)', line)
		res = score()
		if match_single:
			m = match_single.groups()
			nox = ""
			if m[5]:
				nox = m[5]
			return single_result(
				pos = m[0],
				joint = (m[1] == "="),
				name = m[2].strip(),
				score = self.parse_score(m[3], nox),
				prize = m[6])
		elif match_agg:
			m = match_agg.groups()
			return aggregate_result(
				pos = int(m[0].strip()),
				joint = (m[1] == "="),
				name = m[2].strip(),
				scores = m[3].strip().split(" / "),
				score = std_score(int(m[8].strip())),
				prize = m[9].strip())
		elif match_twoteam:
			m = match_twoteam.groups()
			return twoteam_result(
				pos = int(m[0]),
				joint = (m[1] == "="),
				competitors = [ (m[2].strip(), std_score(int(m[3].strip()))),
						(m[4].strip(), std_score(int(m[5].strip())))],
				score = std_score(int(m[6])),
				prize = m[9])
		elif match_threeteam:
			m = match_threeteam.groups()
			return threeteam_result(
				pos = int(m[0]),
				joint = (m[1] == "="),
				competitors = [ (m[2].strip(), std_score(int(m[3]))),
						(m[4].strip(), std_score(int(m[5]))),
						(m[6].strip(), std_score(int(m[7])))],
				score = std_score(int(m[8])),
				prize = m[9].strip())
		elif match_manvman:
			m = match_manvman.groups()
			p = re.match(r'(.+)(Bronze|Silver|Gold)', m[2].strip())
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
		else:
			print >> STDERR, "Line ", self.lineno, ": Warning: unknown score format: '", line, "'\n";
			return bad_result(self.lineno, line)
	
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
