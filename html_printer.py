import result

class bar_graph_printer:
	def __init__(self, out):
		self.bar_width = 300.0
		self.out = out
	
	def newcomp(self, comp):
		minscore = 0
		maxscore = 0
		val = result.score_valuer()
		res = result.score_getter()
		for i in comp.results:
			s = val.get(res.get(i))
			if s < minscore:
				minscore = s
			if s > maxscore:
				maxscore = s
		if maxscore == minscore:
			self.m = 0
		else:
			self.m = self.bar_width / (maxscore - minscore)
	
	def print_bar(self, score):
		s = result.score_valuer().get(score)
		print >>self.out, "<td class='neg'>"
		if s < 0:
			print >>self.out, "<div class='bar' style='width:", str(-self.m*s) + "px'> </div>"
		print >>self.out, "</td><td class='pos'>"
		if s > 0:
			print >>self.out, "<div class='bar' style='width:",  str(self.m*s) + "px'> </div>"
		print >>self.out, "</td>"

class score_printer:
	def __init__(self, out):
		self.out = out
	
	def print_score(self, score, joint):
		self.joint = joint
		score.visit(self)
	
	def visit_std(self, score):
		print >>self.out, "<td class='score'>", score.score(), "</td><td>"
		if self.joint and score.nox() > 0:
			print >>self.out, score.nox(), "x",
		print >>self.out, "</td>"
		
	def visit_time(self, score):
		print >>self.out, "<td class='score'>", score.time(), "</td><td>"
		if self.joint:
			print >>self.out, "(", str(score.score()), ")"
		print >>self.out, "</td>"
	
	def visit_none(self, score):
		print >>self.out, "<td class='score' colspan='2'>No Score</td>"

# Printing class designed to print html stuff with bar graphs, etc.
class printer:
	def __init__(self, out):
		self.out = out
		self.bar_graph = bar_graph_printer(out)
	
	def print_comp(self, comp):
		self.header(comp)
		if comp.type != "manvman":
			self.bar_graph.newcomp(comp)
		for res in comp.results:
			self.print_result(res)
		self.footer(comp)
	
	def header(self, comp):
		print >>self.out, "<h2>", comp.name, "</h2>"
		if comp.entries == 0:
			print >>self.out, "<p class='entries'>No Entries</p>"
			return
		
		print >>self.out, "<p class='entries'>", comp.entries, " Entries</p>"
	
		print >>self.out, "<table>"
		print >>self.out, "<col class='position' />"
		if comp.type=="single":
			print >>self.out, "<col class='personname'/>"
		elif comp.type=="timed":
			print >>self.out, "<col class='personname'/>"
		elif comp.type=="threeteam":
			print >>self.out, "<col class='3scores'/>"
		elif comp.type=="twoteam":
			print >>self.out, "<col class='personname'/>"
			print >>self.out, "<col class='scores'/>"
			print >>self.out, "<col class='personname'/>"
		elif comp.type=="aggregate":
			print >>self.out, "<col class='personname'/>"
			print >>self.out, "<col class='components'/>"		
		
		print >>self.out, "<col class='score'/>"
		print >>self.out, "<col class='nox'/>"
		print >>self.out, "<col class='medal'/>"
		print >>self.out, "<col class='bargraph'/>"
	
	def footer(self, comp):
		print >>self.out, "</table>"
	
	def print_result(self, res):
		self.print_pos(res)
		res.visit(self)
		print >>self.out, "</tr>"

	
	def print_pos(self, res):
		print >>self.out, "<tr onclick='javascript:ClickedThis(this)' class='", res.prize, "'><td>"
		print >>self.out, res.pos
		if res.joint:
			print >>self.out, "="
		print >>self.out, "</td>"
	
	def print_score(self, res):
		score_printer(self.out).print_score(res.score, res.joint)
	
	def print_prize(self, prize):
		print >>self.out, "<td>",
		if prize:
			print >>self.out, prize,
		print >>self.out, "</td>"
	
	def print_bar(self, score):
		self.bar_graph.print_bar(score)
		
	def print_competitor(self, c):
		self.out.write(c[0] + " ("+str(c[1])+")")
	
	def visit_threeteam(self, res):
		print >>self.out, "<td class='threescores'>"
		print >>self.out, res.competitors[0][0], " (", res.competitors[0][1], "), "
		print >>self.out, res.competitors[1][0], " (", res.competitors[1][1], ") &amp "
		print >>self.out, res.competitors[2][0], " (", res.competitors[2][1], ")</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_twoteam(self, res):
		c=res.competitors
		print >>self.out, "<td class='personname1'>",  c[0][0], " </td>"
		print >>self.out, "<td class='scores'> ", c[0][1], " + ", c[1][1], " </td>"
		print >>self.out, "<td class='personname2'> ", c[1][0],  "</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_aggregate(self, res):
		print >>self.out, "<td>", res.name, "</td>"
		print >>self.out, "<td class='components'>", res.scores, " = </td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_single(self, res):
		print >>self.out, "<td>", res.name, "</td>"
		self.print_score(res)
		self.print_prize(res.prize)
		self.print_bar(res.score)
	
	def visit_manvman(self, res):
		print >>self.out, "<td>", res.name, "</td>"
		self.print_prize(res)

class personlist_printer:
	def __init__(self, people, victor_ludorum, out):
		self.out = out
		self.people = people
		self.print_vl = victor_ludorum
	
	def print_people(self):
		print >>self.out, "<table class='sortable'><col class='personname'/><col class='Entries score'/><col class='Gold score'/><col class='Silver score'/><col class='Bronze score'/>"
		if self.print_vl:
			print >>self.out, "<col class='vl score'/>"
		print >>self.out, "<col class='rival'/><tr><th>Name</th><th>Entries</th><th>Golds</th><th>Silvers</th><th>Bronzes</th>"
		if self.print_vl:
			print >>self.out, "<th>Victor<br/>Ludorum</th>"

		for i in self.people:
			print >>self.out, "<tr><td>", i.name, "</td><td class='score'>", i.entries, "</td>",
			print >>self.out, "<td class='score'>", i.prize["Gold"], "</td>",
			print >>self.out, "<td class='score'>", i.prize["Silver"], "</td>",
			print >>self.out, "<td class='score'>", i.prize["Bronze"], "</td>"
			if self.print_vl:
				print >>self.out, "<td class='score'>", i.vlscore(), "</td>"
		print >>self.out, "</table>"
