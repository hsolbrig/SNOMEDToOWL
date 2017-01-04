#!/usr/bin/env python

# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
from typing import Optional
from rdflib import Graph, BNode, URIRef, OWL, RDF
from rdflib.term import Identifier
from rdflib.plugin import plugins as rdflib_plugins, Parser as rdflib_Parser
from rdflib.util import guess_format
from argparse import ArgumentParser
import re
import time

from SNOMEDCTToOWL.SNOMEDToOWLConstants import required_namespaces

# Load two OWL files and compare the output
possible_formats = set(x.name for x in rdflib_plugins(None, rdflib_Parser) if '/' not in str(x.name))


class SNOMEDGraph(Graph):
    def __init__(self, *args, **kwargs):
        Graph.__init__(self, *args, **kwargs)
        [self.bind(e[0], e[1]) for e in required_namespaces.items()]

    def serialize(self, destination=None, format="turtle",
                  base=None, encoding=None, **args) -> str:
        return re.sub(r'^@prefix .* .\n', '',
                      Graph.serialize(self, destination, format,
                                      base, encoding, **args).decode(), flags=re.MULTILINE).strip()


class Timer:
    def __init__(self, enabled: bool=True):
        self._t0 = time.time()
        self.enabled = enabled

    def elapsed(self) -> str:
        return time.time() - self._t0

    def time(self, msg: str) -> None:
        if self.enabled:
            print('({:.2f}) - '.format(self.elapsed()) + msg)


def complete_definition(subj: Identifier,
                        source_graph: Graph,
                        target_graph: Optional[SNOMEDGraph] = None) -> SNOMEDGraph:
    """
    Add a full definition for the supplied subject, following any object bnodes, to target_graph
    :param subj: URI or BNode for subject
    :param source_graph: Graph containing defininition
    :param target_graph: Graph to carry definition
    :return: target_graph
    """
    if not target_graph:
        target_graph = SNOMEDGraph()
    for p, o in source_graph.predicate_objects(subj):
        target_graph.add((subj, p, o))
        if isinstance(o, BNode):
            complete_definition(o, source_graph, target_graph)
    return target_graph


def genargs() -> ArgumentParser:
    """
    Generate an input string parser
    :return: parser
    """
    parser = ArgumentParser(description="Compare two OWL RDF files")
    parser.add_argument("file1", help="RDF File 1")
    parser.add_argument("file2", help="RDF File 2")
    parser.add_argument("-f1", help="File 1 format", choices=possible_formats)
    parser.add_argument("-f2", help="File 2 format", choices=possible_formats)
    parser.add_argument("-p", help="Print progress and timing information", action="store_true")
    parser.add_argument("-nh", "--noheader", help="Omit ontology header comparison", action="store_true")
    return parser


def main(argv):
    opts = genargs().parse_args(argv)
    t = Timer(opts.p)
    t.time("Loading g1")
    g1 = Graph().parse(file=open(opts.file1), format=opts.f1 if opts.f1 else guess_format(opts.file1))
    t.time("Loading g2")
    g2 = Graph().parse(file=open(opts.file2), format=opts.f2 if opts.f2 else guess_format(opts.file2))
    t.time("g1 subjects")
    g1_subjs = set([s for s in g1.subjects() if isinstance(s, URIRef)])
    t.time("g2 subjects")
    g2_subjs = set([s for s in g2.subjects() if isinstance(s, URIRef)])
    t.time("analysis")
    for s in g1_subjs - g2_subjs:
        print("\nMISSED: ", end='')
        print(complete_definition(s, g1).serialize(format="turtle"))
    for s in g2_subjs - g1_subjs:
        print("\nADDED: ", end='')
        print(complete_definition(s, g2).serialize(format="turtle"))
    for s in g1_subjs.intersection(g2_subjs):
        if not opts.noheader or OWL.Ontology not in g1.objects(s, RDF.type):
            s_in_g1 = complete_definition(s, g1)
            s_in_g2 = complete_definition(s, g2)
            if not s_in_g1.isomorphic(s_in_g2):
                print("\nFILE 1:", end='')
                print(s_in_g1.serialize(format="turtle"))
                print("\nFILE 2:", end='')
                print(s_in_g2.serialize(format="turtle"))
    t.time("Done")
