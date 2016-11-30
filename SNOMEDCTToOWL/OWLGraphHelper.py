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


# A collection of utilities for managing OWL Graphs
from typing import Tuple
from rdflib import Graph, BNode, RDF, OWL, URIRef
from rdflib.collection import Collection
from rdflib.term import Node
from SNOMEDCTToOWL.SNOMEDToOWLConstants import Role_group, SCT


def as_uri(sctid: int) -> URIRef:
    """
    Convert an sctid to a URI
    :param sctid:
    :return: the URI for the sctid
    """
    return SCT[str(sctid)]


def intersection(g: Graph) -> Tuple[BNode, Collection]:
    """
    Generate an intersection class
    :param g: target graph
    :return: BNode that represents the intersection and the actual collection to append individual elements to
    """
    subj = BNode()
    collection_node = BNode()
    coll = Collection(g, collection_node)
    g.add((subj, RDF.type, OWL.Class))
    g.add((subj, OWL.intersectionOf, collection_node))
    return subj, coll


def existential_restriction(g: Graph, predicate: URIRef, target: URIRef) -> BNode:
    """
    Generate an existential restriction from the supplied relationship
    :param g: target graph
    :param predicate: predicate
    :param target: target
    :return: BNode that represents the entire restriction
    """
    restriction = BNode()
    g.add((restriction, RDF.type, OWL.Restriction))
    g.add((restriction, OWL.onProperty, predicate))
    g.add((restriction, OWL.someValuesFrom, target))
    return restriction


def role_group(g: Graph, target: Node) -> BNode:
    """
    Surround target with a role group
    :param g: target Graph
    :param target: target URI or BNODE
    :return: BNode that represents entire restriction
    """
    subj = BNode()
    g.add((subj, RDF.type, OWL.Restriction))
    g.add((subj, OWL.onProperty, Role_group))
    g.add((subj, OWL.someValuesFrom, target))
    return subj
