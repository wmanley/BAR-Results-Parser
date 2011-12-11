#!/usr/bin/env python
import csv
import sys
import itertools
from itertools import izip
from collections import namedtuple
from result import *
import jim_printer
import optparse

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

def parse(rows):
    for meta, rows in iterate_competitions(rows):
        if meta.type == "Single":
            parser = Single()
        else:
            sys.stderr.write("Skipping competition '%s': Unknown type '%s'\n" % (meta.name, meta.type))
            continue
        parser = Single()
        comp = competition(meta.name, "single", len(rows))
        comp.results = list(parser.parse(rows))
        yield comp

class aggregate:
    name = "aggregate"
    header_regex = r'Position\s+Name\s+Score\(stages 1/2/3/4/Tot\)\s+Medal'
    score_regex = r'(\d+)(=?)\s+(\D*)\s+((\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-))\s*\/\s*(\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
    
    def build(self, m):
        return aggregate_result(
            pos = int(m[0].strip()),
            joint = (m[1] == "="),
            name = m[2].strip(),
            scores = m[3].strip().split(" / "),
            score = std_score(int(m[8].strip())),
            prize = m[9].strip())

class threeteam:
    name = "threeteam"
    header_regex = r'Position\s+Threesome\s+Score'
    score_regex = r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\),\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
    def build(self, m):
        return threeteam_result(
            pos = int(m[0]),
            joint = (m[1] == "="),
            competitors = [ (m[2].strip(), std_score(int(m[3]))),
                    (m[4].strip(), std_score(int(m[5]))),
                    (m[6].strip(), std_score(int(m[7])))],
            score = std_score(int(m[8])),
            prize = m[9].strip())

class twoteam:
    name = "twoteam"
    header_regex = r'Position\s+Pair\s+Score'
    score_regex = r'(\d+)(=?)\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)(\s+\(Age \d+\))?((\s+(Bronze|Silver|Gold|Wine))?)\s*$'
    def build(self, m):
        return twoteam_result(
            pos = int(m[0]),
            joint = (m[1] == "="),
            competitors = [ (m[2].strip(), std_score(int(m[3].strip()))),
                    (m[4].strip(), std_score(int(m[5].strip())))],
            score = std_score(int(m[6])),
            prize = m[9])

def main(argv):
    parser = optparse.OptionParser("usage: %prog [options] input-file.csv")
    (options, args) = parser.parse_args(argv[1:])
    if len(args) != 1:
        parser.error("wrong number of arguments")
        return 1
    input_csv_filename = args[0]

    printer = jim_printer.printer(sys.stdout)
    parsed = parse(csv.reader(open(input_csv_filename, "r")))
    for i in parsed:
        printer.print_comp(i)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

