#!/usr/bin/env python
import csv
import sys
import itertools
from itertools import izip
from collections import namedtuple
from result import *
import jim_printer
import html_printer
import jim_html_printer
import optparse
import re
import person

class ParseError(Exception):
    def __init__(self, lineno, description):
        self.lineno = lineno
        self.description = description

def iterate_competitions(rows):
    """
    Iterator adaptor which will stop at the end of a competition (i.e. blank line)
    
    >>> list(iterate_competitions([]))
    []
    >>> list(iterate_competitions([['Eroff'],['a'],['b'],[''],['Hermges'],['a']]))
    [(('Eroff', 'Single'), [['a'], ['b']]), (('Hermges', 'Single'), [['a']])]
    """
    CompMetadata = namedtuple('CompMetadata', 'name type')
    metadata = None
    l = []
    for row in rows:
        blank = True
        for i in row:
            if i != '':
                blank = False
        if blank and metadata:
            yield (metadata, l)
            metadata = None
        elif not blank and not metadata:
            print row
            metadata = CompMetadata(row[0], "Single" if row[1] == "" else row[1])
            l = []
        elif not blank and metadata:
            l.append(row)
    if metadata:
        yield (metadata, l)

medals = [
    ("Gold", 0.03),
    ("Silver", 0.07),
    ("Bronze", 0.1)
]

def award_medal(position, no_entrants):
    """
    >>> award_medal(1, 4)
    ''
    >>> award_medal(1, 5)
    'Bronze'
    >>> award_medal(2, 5)
    ''
    """
    n = 0
    for m in medals:
        n += int(m[1]*no_entrants+0.5)
        if position <= n:
            return m[0]
    return ""

def assign_positions(iterable):
    """
    >>> list(assign_positions([]))
    []
    >>> list(assign_positions([{"color": "Tabby", "score": 3}]))
    [{'color': 'Tabby', 'joint': False, 'score': 3, 'pos': 1}]
    >>> list(assign_positions([{"name": "a", "score": 1}, {"name": "b", "score": 2}, {"name": "c", "score": 2}, {"name": "d", "score": 4} ]))
    [{'joint': False, 'score': 1, 'name': 'a', 'pos': 1}, {'joint': True, 'score': 2, 'name': 'b', 'pos': 2}, {'joint': True, 'score': 2, 'name': 'c', 'pos': 2}, {'joint': False, 'score': 4, 'name': 'd', 'pos': 4}]
    """
    last = None
    for i, n in izip(iterable, itertools.count(1)):
        if last and i["score"] == last["score"]:
            i["pos"] = last["pos"]
            i["joint"] = True
            last["joint"] = True
        else:
            i["pos"] = n
            i["joint"] = False
        if last:
            yield last
        last = i
    if last:
        yield last

class Single:
    dependencies = []
    def parse_row(self, row):
        return dict(name=row[0], score=std_score(int(row[1]), int(row[2] if row[2] != '' else '0')))
    def parse(self, rows):
        results = sorted([self.parse_row(x) for x in rows], lambda a, b: cmp(a["score"], b["score"]))
        results.reverse()
        for i in assign_positions(results):
            pass
        for i in results:
		    yield single_result(
		        prize = award_medal(i["pos"], len(results)),
		        **i)

class Smith:
    def parse_row(self, row):
        score = no_score() if row[1] == "N/S" else time_score(float(row[1]), int(row[2]))
        return dict(name=row[0], score=score)
    def parse(self, rows):
        results = sorted([self.parse_row(x) for x in rows], lambda a, b: cmp(a["score"], b["score"]))
        results.reverse()
        for i in assign_positions(results):
            pass
        for i in results:
            yield single_result(
                prize = award_medal(i["pos"], len(results)),
                **i)

class Pairs:
    def __init__(self, source_comp_name, lookup_table):
        self.source_comp_name = source_comp_name
        self.dependencies = [ source_comp_name ]
        self.lookup_table = lookup_table
    def moo(self, row):
        for person in row:
            score = self.lookup_table.get((self.source_comp_name, person))
            if person == "":
                pass
            elif score is None:
                sys.stderr.write('%s did not compete in competition %s required for a pairs competiton\n' % (person, self.source_comp_name))
                yield namedtuple('PreliminaryResult', 'name score')(person, no_score())
            else:
                yield namedtuple('PreliminaryResult', 'name score')(person, score)
    def moo2(self, row):
        m = list(self.moo(row))
        return { "competitors": m, "score": sum([ x.score for x in m ], std_score(0)) }
    def parse(self, rows):
        processed = [ self.moo2(x) for x in rows ]
        processed.sort(key=lambda x: x["score"], reverse=True)
        wine_won = len(processed) > 1
        for i in assign_positions(processed):
            pass
        for i in processed:
            no_competitors = len(i["competitors"])
            if no_competitors not in [2, 3]:
                sys.stderr.write('Error: "Team" comprised of %d members: %s\n' % (no_competitors, str(i['competitors'])))
            elif isinstance(i["score"], no_score):
                sys.stderr.write('Warning: No score for team %s\n' % str(i['competitors']))
            else:
                yield {2: twoteam_result,
                       3: threeteam_result}[no_competitors](
                           prize = "Wine" if wine_won else "",
                           **i)
                wine_won = False

class Freundschaftschiessen:
    def parse(self, rows):
        results = {} # { team: [results] }
        for i in rows:
            (team, competitor, score) = i
            results[team] = (competitor, score)
            

class Aggregate:
    def __init__(self, constituent_competitions, lookup_table):
        self.constituent_competitions = constituent_competitions
        self.dependencies = constituent_competitions
        self.lookup_table = lookup_table
    def moo(self, rows):
        for row in rows:
            name = row[0]
            scores = [ self.lookup_table.get((x, name), no_score()) for x in self.constituent_competitions ]
            score = sum(scores, std_score(0))
            if isinstance(score, no_score):
                sys.stderr.write("%s had incomplete aggregate %s\n" % (name, str(self.constituent_competitions)))
            else:
                yield {"name": name, "scores": [str(x) for x in scores], "score": score}
    def parse(self, rows):
        results = sorted(list(self.moo(rows)), key=lambda x: x["score"], reverse=True)
        for x in assign_positions(results):
            pass
        for i in results:
            yield aggregate_result(
		        prize = award_medal(i["pos"], len(results)),
		        **i)

def parse(rows):
    lookup_table = {}
    for meta, rows in iterate_competitions(rows):
        if meta.type == "Single":
            parser = Single()
            name = meta.name
        elif meta.type == "Smith":
            parser = Smith()
            name = meta.name
        elif meta.type == "Pair":
            m = re.match("(.+) \((.*)\)", meta.name)
            if m:
                (name, source_comp) = m.groups()
                parser = Pairs(source_comp, lookup_table)
            else:
                sys.stderr.write('Pairs competition "%s" is not well formed!\n' % meta.name)
                continue
        elif meta.type == "Aggregate":
            m = re.match("(.+) \((.*)\)", meta.name)
            if m:
                name = m.group(1)
                constituent_competitions = m.group(2).split(", ")
                parser = Aggregate(constituent_competitions, lookup_table)
            else:
                sys.stderr.write('Aggregate competition "%s" is not well formed!\n' % meta.name)
                continue
        else:
            sys.stderr.write("Skipping competition '%s': Unknown type '%s'\n" % (meta.name, meta.type))
            continue
        results = list(parser.parse(rows))
        comp = competition(name, "single", len(results), results)
        if meta.type != 'Pair':
            lookup_table.update([((name, x.name), x.score) for x in comp.results])
        yield comp

def main(argv):
    parser = optparse.OptionParser("usage: %prog [options] input-file.csv")
    parser.add_option("-o", "--output-format", dest="output_format",
                      choices=["graph-html", "jim-html", "jim-text"], default="jim-text")
    parser.add_option("--print-summary", dest="print_summary", action="store_true")
    (options, args) = parser.parse_args(argv[1:])
    if len(args) != 1:
        parser.error("wrong number of arguments")
        return 1
    input_csv_filename = args[0]
    output_stream = sys.stdout

    output_module = {"jim-text": jim_printer,
                     "graph-html": html_printer,
                     "jim-html": jim_html_printer}[options.output_format]
    printer = output_module.printer(output_stream)
    parsed = list(parse(csv.reader(open(input_csv_filename, "r"))))

    output_module.prelude(output_stream, "Results")
    for i in parsed:
        printer.print_comp(i)

    if options.print_summary:
        peo = person.analyser()
        for i in parsed:
            for k in i.results:
                peo.analyse_result(k)
        pp = output_module.personlist_printer(peo.people.values(), True, output_stream)
        pp.print_people()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

