
# Printing class intended to reproduce the results as created by Jim
class printer:
	def __init__(self, out):
		self.out = out

	def print_comp(self, comp):
		self.header(comp)
		for res in comp.results:
			self.print_result(res)
		self.out.write("</table>")

	def header(self, comp):
		headings = {
			"single":    "<tr><th>Position</th>\t<th>Name</th>\t<th>Score</th>\t<th>Medal</th></tr>",
			"timed":     "<tr><th>Position</th>\t<th>Name</th>\t<th>Time</th>\t<th>Medal</th></tr>",
			"threeteam": "<tr><th>Position</th>\t<th>Threesome</th>\t<th>Score</th></tr>",
			"twoteam":   "<tr><th>Position</th>\t<th>Pair</th>\t<th>Score</th></tr>",
			"aggregate": "<tr><th>Position</th>\t<th>Name</th>\t<th>Score(stages 1/2/3/4/Tot)</th>\t<th>Medal</th></tr>"
		}
		self.out.write("<h2>%s</h2>\n<p>%d %s</p>\n<table>\n\t%s\n" % (comp.name, comp.entries, "Entries" if comp.entries > 1 else "Entry", headings.get(comp.type)))

	def print_result(self, res):
		self.out.write("<tr>")
		self.print_pos(res)
		res.visit(self)
		self.print_prize(res)
		self.out.write("</tr>\n")

	def print_pos(self, res):
		self.out.write("<td>%s%s</td>\t" % (res.pos, "=" if res.joint else ""))

	def print_prize(self, res):
		self.out.write("<td>%s</td>" % (res.prize if res.prize else ""))

	def visit_threeteam(self, res):
		c = res.competitors
		self.out.write("<td>%s (%s), %s (%s) & %s (%s)</td>\t<td>%s</td>" % (c[0][0], str(c[0][1]), c[1][0], str(c[1][1]), c[2][0], str(c[2][1]), str(res.score)))

	def visit_twoteam(self, res):
		c = res.competitors
		self.out.write("<td>%s (%s) & %s (%s)</td>\t<td>%s</td>" % (c[0][0], c[0][1], c[1][0], c[1][1], str(res.score)))

	def visit_aggregate(self, res):
		self.out.write("<td>%s</td>\t<td>%s/%s</td>" % (res.name, "/".join(res.scores), str(res.score)))

	def visit_single(self, res):
		self.out.write("<td>%s</td>\t<td>%s</td>" % (res.name, str(res.score)))

	def visit_manvman(self, res):
		self.out.write(res.name)

