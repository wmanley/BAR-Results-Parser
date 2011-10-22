
# Printing class intended to reproduce the results as created by Jim
class printer:
	def __init__(self, out):
		self.out = out
	
	def print_comp(self, comp):
		self.header(comp)
		for res in comp.results:
			self.print_result(res)
		self.out.write("\n")
	
	def header(self, comp):
		headings = {
			"single":    "Position\tName\tScore\tMedal",
			"timed":     "Position\tName\tTime\tMedal",
			"threeteam": "Position\tThreesome\tScore",
			"twoteam":   "Position\tPair\tScore",
			"aggregate": "Position\tName\tScore(stages 1/2/3/4/Tot)\tMedal"
		}
		self.out.write("%s\n%d Entr%s\n%s\n" % (comp.name, comp.entries, "ies" if comp.entries > 1 else "y", headings.get(comp.type)))
	
	def print_result(self, res):
		self.print_pos(res)
		res.visit(self)
		self.print_prize(res)
		self.out.write("\n")
	
	def print_pos(self, res):
		self.out.write("%s%s\t" % (res.pos, "=" if res.joint else ""))
	
	def print_prize(self, res):
		if res.prize:
			self.out.write("\t" + res.prize)
	
	def visit_threeteam(self, res):
		c = res.competitors
		self.out.write("%s (%s), %s (%s) & %s (%s)\t%s" % (c[0][0], str(c[0][1]), c[1][0], str(c[1][1]), c[2][0], str(c[2][1]), str(res.score)))
	
	def visit_twoteam(self, res):
		c = res.competitors
		self.out.write("%s (%s) & %s (%s)	%s" % (c[0][0], c[0][1], c[1][0], c[1][1], str(res.score)))
	
	def visit_aggregate(self, res):
		self.out.write("%s\t%s/%s" % (res.name, "/".join(res.scores), str(res.score)))

	def visit_single(self, res):
		self.out.write("%s\t%s" % (res.name, str(res.score)))

	def visit_manvman(self, res):
		self.out.write(res.name)

