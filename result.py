#!/usr/bin/python

import sys

class score:
	def visit(self, other):
		other.visit_score(self)

class std_score(score):
	def __init__(self, score, nox=0):
		self._score = score
		self._nox = nox
	def score(self):
		return self._score
	def nox(self):
		return self._nox
	def visit(self, other):
		other.visit_std(self)
	def __str__(self):
		if self.nox() == 0:
			return str(self.score())
		else:
			return str(self.score()) + " " + str(self.nox()) + "x"

class time_score(score):
	def __init__(self):
		self._time = 0
		self._score = null_score()
	def time(self):
		return self._time
	def score(self):
		return self._score
	def visit(self, other):
		other.visit_time(self)
	def __str__(self):
		return str(self.time()) + "s " + " (" + str(self.score) + ")"

class no_score(score):
	def visit(self, other):
		other.visit_none(self)
	def __str__(self):
		return ""

class result:
	def __init__(self, pos, joint, prize):
		self.pos = pos
		self.prize = prize
		self.joint = joint
	def visit(self, other):
		other.visit_result(self)

class threeteam_result(result):
	def __init__(self, pos, joint, competitors, score, prize):
		result.__init__(self, pos, joint, prize)
		self.competitors = competitors
		self.score = score
	def visit(self, other):
		other.visit_threeteam(self)

class twoteam_result(result):
	def __init__(self, pos, joint, competitors, score, prize):
		result.__init__(self, pos, joint, prize)
		self.competitors = competitors
		self.score = score
	def visit(self, other):
		other.visit_twoteam(self)

class aggregate_result(result):
	def __init__(self, pos, joint, name, scores, score, prize):
		result.__init__(self, pos, joint, prize)
		self.name = name
		self.scores = scores
		self.score = score
	def visit(self, other):
		other.visit_aggregate(self)

class single_result(result):
	def __init__(self, pos, joint, name, score, prize):
		result.__init__(self, pos, joint, prize)
		self.name = name
		self.score = score
	def visit(self, other):
		other.visit_single(self)

class manvman_result(result):
	def __init__(self, pos, joint, name, prize):
		result.__init__(self, pos, joint, prize)
		self.name = name
	def visit(self, other):
		other.visit_manvman(self)

class bad_result(result):
	def __init__(self, lineno, data):
		result.__init__(self, 0, 0, "")
		self.data = data
	def visit(self, other):
		other.visit_bad(self)

class competition:
	def __init__(self):
		self.entries = 0
		self.name = ""
		self.results = []
		self.type = "unknown"

class personlister:
	def get(self, res):
		res.visit(self)
		return self.people
	
	def visit_threeteam(self, res):
		self.people = [i[0] for i in res.competitors]
	
	def visit_twoteam(self, res):
		self.people = [i[0] for i in res.competitors]
	
	def visit_aggregate(self, res):
		self.people = [res.name]
	
	def visit_single(self, res):
		self.people = [res.name]
		
	def visit_manvman(self, res):
		self.people = [res.name]
	
	def visit_bad(self, res):
		self.people = []


