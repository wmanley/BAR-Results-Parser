
# Printing class intended to reproduce the results as created by Jim
class printer:
	def __init__(self, out):
		self.out = out
	
	def print_comp(self, comp):
		self.header(comp)
		for res in comp.results:
			self.print_result(res)
	
	def header(self, comp):
		print >>self.out, comp.name, "\n", comp.entries, " Entries"
		if comp.type=="single":
			print "Position\tName\tScore\tMedal"
		elif comp.type=="timed":
			print "Position\tName\tTime\tMedal"
		elif comp.type=="threeteam":
			print "Position\tThreesome\tScore"
		elif comp.type=="twoteam":
			print "Position\tPair\tScore"
		elif comp.type=="aggregate":
			print "Position\tName\tScore(stages 1/2/3/4/Tot)\tMedal"
	
	def print_result(self, res):
		self.print_pos(res)
		res.visit(self)
		self.print_prize(res)
		print
	
	def print_pos(self, res):
		self.out.write(str(res.pos))
		if res.joint:
			print "=",
		print "\t",
	
	def print_prize(self, res):
		if res.prize:
			print >>self.out, "\t", res.prize,
	
	def print_competitor(self, c):
		self.out.write(c[0] + " ("+str(c[1])+")")

	def visit_threeteam(self, res):
		self.print_competitor(res.competitors[0])
		print >>self.out, ", ",
		self.print_competitor(res.competitors[1])
		print >>self.out, " & ",
		self.print_competitor(res.competitors[2])
		print "\t", str(res.score), 
	
	def visit_twoteam(self, res):
		self.print_competitor(res.competitors[0])
		print " & ",
		self.print_competitor(res.competitors[1])
		print "\t", str(res.score),
	
	def visit_aggregate(self, res):
		print >>self.out, res.name, "\t", 
		for i in res.scores:
			print >>self.out, i, "/",
		print res.score,

	def visit_single(self, res):
		print >>self.out, res.name, "\t", res.score, 

	def visit_manvman(self, res):
		print >>self.out, res.name,

