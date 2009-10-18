
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

class bar_graph_printer:
	def __init__(self):
		self.bar_width = 300.0
	
	def newcomp(self, comp):
		minscore = 0
		maxscore = 0
		val = score_valuer()
		for i in comp.results:
			s = val.get(i.score)
			if s < minscore:
				minscore = s
			if s > maxscore:
				maxscore = s
		if maxscore == minscore:
			self.m = 0
		else:
			self.m = self.bar_width / (maxscore - minscore)
	
	def print_bar(self, score):
		s = score_valuer().get(score)
		print "<td class='neg'>"
		if s < 0:
			print "<div class='bar' style='width:", str(-self.m*s) + "px'> </div>"
		print "</td><td class='pos'>"
		if s > 0:
			print "<div class='bar' style='width:",  str(self.m*s) + "px'> </div>"
		print "</td>"

class score_printer:
	def print_score(self, score, joint):
		self.joint = joint
		score.visit(self)
	
	def visit_std(self, score):
		print "<td class='score'>", score.score(), "</td><td>"
		if self.joint and score.nox() > 0:
			print score.nox(), "x",
		print "</td>"
		
	def visit_time(self, score):
		print "<td class='score'>", score.time(), "</td><td>"
		if self.joint:
			print "(", str(score.score()), ")"
		print "</td>"
	
	def visit_none(self, score):
		print "<td class='score' colspan='2'>No Score</td>"

# Printing class designed to print html stuff with bar graphs, etc.
class printer:
	def __init__(self, out):
		self.out = out
		self.bar_graph = bar_graph_printer()
	
	def print_comp(self, comp):
		self.header(comp)
		if comp.type != "manvman":
			self.bar_graph.newcomp(comp)
		for res in comp.results:
			self.print_result(res)
		self.footer(comp)
	
	def header(self, comp):
		print "<h2>", comp.name, "</h2>"
		if comp.entries == 0:
			print "<p class='entries'>No Entries</p>"
			return
		
		print "<p class='entries'>", comp.entries, " Entries</p>"
	
		print "<table>"
		print "<col class='position' />"
		if comp.type=="single":
			print "<col class='personname'/>"
		elif comp.type=="timed":
			print "<col class='personname'/>"
		elif comp.type=="threeteam":
			print "<col class='3scores'/>"
		elif comp.type=="twoteam":
			print "<col class='personname'/>"
			print "<col class='scores'/>"
			print "<col class='personname'/>"
		elif comp.type=="aggregate":
			print "<col class='personname'/>"
			print "<col class='components'/>"		
		
		print "<col class='score'/>"
		print "<col class='nox'/>"
		print "<col class='medal'/>"
		print "<col class='bargraph'/>"
	
	def footer(self, comp):
		print "</table>"
	
	def print_result(self, res):
		self.print_pos(res)
		res.visit(self)
		print "</tr>"

	
	def print_pos(self, res):
		print "<tr onclick='javascript:ClickedThis(this)' class='", res.prize, "'><td>"
		print res.pos
		if res.joint:
			print "="
		print "</td>"
	
	def print_score(self, res):
		score_printer().print_score(res.score, res.joint)
	
	def print_prize(self, prize):
		print "<td>",
		if prize:
			print prize,
		print "</td>"
	
	def print_bar(self, score):
		self.bar_graph.print_bar(score)
		
	def print_competitor(self, c):
		self.out.write(c[0] + " ("+str(c[1])+")")
	
	def visit_threeteam(self, res):
		print "<td class='threescores'>"
		print res.competitors[0][0], " (", res.competitors[0][1], "), "
		print res.competitors[1][0], " (", res.competitors[1][1], ") &amp "
		print res.competitors[2][0], " (", res.competitors[2][1], ")</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_twoteam(self, res):
		c=res.competitors
		print "<td class='personname1'>",  c[0][0], " </td>"
		print "<td class='scores'> ", c[0][1], " + ", c[1][1], " </td>"
		print "<td class='personname2'> ", c[1][0],  "</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_aggregate(self, res):
		print "<td>", res.name, "</td>"
		print "<td class='components'>", res.scores, " = </td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_single(self, res):
		print "<td>", res.name, "</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_manvman(self, res):
		print "<td>", res.name, "</td>"
		self.print_prize(res)

class personlist_printer:
	def __init__(self, people, victor_ludorum):
		self.people = people
		self.print_vl = victor_ludorum
	
	def print_people(self):
		print "<table class='sortable'><col class='personname'/><col class='Entries score'/><col class='Gold score'/><col class='Silver score'/><col class='Bronze score'/>"
		if self.print_vl:
			print "<col class='vl score'/>"
		print "<col class='rival'/><tr><th>Name</th><th>Entries</th><th>Golds</th><th>Silvers</th><th>Bronzes</th>"
		if self.print_vl:
			print "<th>Victor<br/>Ludorum</th>"

		for i in self.people:
			print "<tr><td>", i.name, "</td><td class='score'>", i.entries, "</td>",
			print "<td class='score'>", i.prize["Gold"], "</td>",
			print "<td class='score'>", i.prize["Silver"], "</td>",
			print "<td class='score'>", i.prize["Bronze"], "</td>"
			if self.print_vl:
				print "<td class='score'>", i.vlscore(), "</td>"
		print "</table>"
