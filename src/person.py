import result
import sys

class person:
	def __init__(self, name):
		self.name = name
		self.entries = 0
		self.prize = {"Bronze": 0, "Silver": 0, "Gold": 0, "Wine": 0}
		self.silvers = 0
	def vlscore(self):
		return self.prize["Bronze"] + self.prize["Silver"]*3 + self.prize["Gold"]*5
	def __str__(self):
		return str(self.name)

class analyser:
	def __init__(self):
		self.people = {}
	
	def analyse_result(self, res):
		p = result.personlister()
		for i in p.get(res):
			self.do_person(i, res.prize)
	
	def do_person(self, p, prize):
		if p not in self.people.keys():
			self.people[p] = person(p)
		if prize:
			self.people[p].prize[prize] = self.people[p].prize[prize] + 1
		self.people[p].entries = self.people[p].entries + 1

