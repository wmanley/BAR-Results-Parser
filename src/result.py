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
	def __cmp__(self, other):
		if isinstance(other, no_score):
			return 1
		elif self.score() == other.score():
			return cmp(self.nox(), other.nox())
		else:
			return cmp(self.score(), other.score())
	def __add__(self, other):
		if self is None:
			return self
		elif isinstance(other, no_score):
			return no_score()
		else:
			return std_score(self.score() + other.score(), self.nox() + other.nox())

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
	def __cmp__(self, other):
		if self.time() == other.time():
			return cmp(self.score(), other.score())
		else:
			return -cmp(self.time(), other.time())

class no_score(score):
	def visit(self, other):
		other.visit_none(self)
	def __str__(self):
		return ""
	def __cmp__(self, other):
		if isinstance(other, no_score):
			return 0
		else:
			return -1
	def __add__(self, other):
		return no_score()

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
	def __init__(self, name = "", ctype="unknown", entries = 0):
		self.entries = entries
		self.name = name
		self.results = []
		self.type = ctype

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

class score_getter:
	def get(self, res):
		res.visit(self)
		return self.score
	
	def visit_threeteam(self, res):
		self.score = res.score
	
	def visit_twoteam(self, res):
		self.score = res.score
	
	def visit_aggregate(self, res):
		self.score = res.score
	
	def visit_single(self, res):
		self.score = res.score
		
	def visit_manvman(self, res):
		self.score = std_score(res.pos)
	
	def visit_bad(self, res):
		self.score = no_score()

class score_valuer:
	def get(self, score):
		score.visit(self)
		return self.value
	
	def visit_std(self, score):
		self.value = score.score()
		
	def visit_time(self, score):
		self.value = score.time()
	
	def visit_none(self, score):
		self.value = 0
