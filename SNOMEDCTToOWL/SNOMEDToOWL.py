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
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
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
import csv
import os
from typing import Optional, Set
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.collection import Collection
from rdflib.namespace import NAME_START_CATEGORIES

from SNOMEDCTToOWL.RF2Files import Concept
from SNOMEDCTToOWL.RF2Files.RF2File import RF2File
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *
from SNOMEDCTToOWL.RF2Files.Concept import Concepts
from SNOMEDCTToOWL.RF2Files.Description import Descriptions
from SNOMEDCTToOWL.RF2Files.Transitive import Transitive
from SNOMEDCTToOWL.RF2Files.Relationship import Relationships, Relationship
from SNOMEDCTToOWL.RF2Files.Language import Languages
from SNOMEDCTToOWL.TransformationContext import TransformationContext
from SNOMEDCTToOWL.OWLGraphHelper import as_uri, role_group, intersection, existential_restriction


class OWLGraph(Graph):
    """
    An OWLGraph is a representation of a collection of SNOMED CT RF2 files in OWL format
    """

    def __init__(self, transformation_context: TransformationContext, directory: Optional[str] = None, *args, **kwargs):
        """
        Construct an OWL representation of SNOMED CT RF2 content
        :param transformation_context: Context parameters used for construction
        :param directory: Directory for files.  Multiple directories can be added using the add_directory function
        :param args: additional positional arguments for rdflib Graph constructor
        :param kwargs: additional keyword arguments for rdflib Graph constructor
        """
        Graph.__init__(self, *args, **kwargs)

        self._context = transformation_context

        self._concepts = Concepts()
        self._relationships = Relationships()
        self._descriptions = Descriptions()
        self._languages = Languages()
        self._transitive = Transitive()

        if directory:
            self.add_directory(directory)

    def add_directory(self, directory: str) -> None:
        """
        Add a directory that contains a set of snapshot files.  Recursively descend in the directory adding all of
        the files to the list of files to evaluate
        :param directory: path to directory
        """
        print("Creating transitive file")
        for subdir, _, files in os.walk(directory):
            for file in files:
                self._proc_transitive_file(file, subdir)

        for subdir, _, files in os.walk(directory):
            for file in files:
                self._proc_file(file, subdir, self._concepts) or \
                    self._proc_file(file, subdir, self._descriptions) or \
                    self._proc_file(file, subdir, self._languages) or \
                    self._proc_file(file, subdir, self._relationships)

    def _proc_transitive_file(self, file: str, filedir: str) -> None:
        """
        Add the contents of a relationship file into the transitive file
        :param file: file name
        :param filedir: file directory
        """
        if Transitive.filtr(file):
            with open(os.path.join(filedir, file)) as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                [self._transitive.add(row) for row in reader
                 if int(row['active']) == 1 and int(row['typeId']) == Is_a_sctid]

    def _proc_file(self, file: str, filedir: str, cls: RF2File) -> bool:
        """
        See whether file should be processed for class cls.
        :param file: File name
        :param filedir: Containing directory
        :param cls: Target class
        :return: true if processed, false if not for this class
        """
        if cls.filtr(file, self._context):
            print("Processing %s" % file)
            with open(os.path.join(filedir, file)) as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                [cls.add(row, self._context, self._transitive) for row in reader if int(row['active']) == 1]
            return True
        return False

    def add_transformation_namespaces(self):
        """
        Add the required namespaces to the graph
        """
        [self.bind(e[0], e[1]) for e in required_namespaces.items()]

    def add_ontology_header(self) -> None:
        """
        Add the ontology header to the graph
        """
        module_uri = SCTM[str(self._context.MODULE)]
        self.add((module_uri, RDF.type, OWL.Ontology))
        self.add((module_uri, RDFS.label, Literal(self._context.MODULE_LABEL)))
        self.add((module_uri, OWL.versionIRI,
                  SCTF[str(module_uri + '/version/' + str(self._context.VERSION))]))
        self.add((module_uri, OWL.versionInfo, Literal(self._context.VERSION_DESCRIPTION)))
        self.add((module_uri, RDFS.comment, Literal(self._context.MODULE_DESCRIPTION)))
        self.add((module_uri, RDFS.comment, Literal(self._context.MODULE_COPYRIGHT)))

    def add_object_property_declarations(self) -> None:
        """
        All active descendants of 410662002 | Concept model attribute | with the exception of 116680003|is a|
        are represented as instances of owl:ObjectProperty. All object property concepts are included in the OWL
        file no matter which module they are defined in.
        """
        print("Adding properties")
        [self.add_concept(subj) for subj in self._concepts.properties]

    def add_module_definitions(self) -> None:
        """
        Declare all active concepts whose moduleId matches $MODULE and who are:
        a) not descendants of 160237007 |Linkage concept| as OWL Classes or
        b) ARE descendants of 410662002 |Concept model attribute|
        """
        print("Adding concepts")
        [self.add_concept(subj) for subj in self._concepts.members]

    def add_concept(self, concept: Concept) -> None:
        """
        Add Class/ObjectProperty declaration
        :param concept: concept to add
        """
        concept_uri = as_uri(concept.id)
        typ = OWL.ObjectProperty if self._transitive.is_descendant_of(concept.id, Concept_model_attribute_sctid) \
            else OWL.Class

        # Add the concept itself
        self.add((concept_uri, RDF.type, typ))

        # Generate an rdfs:label for the English FSN of the concept
        self.add((concept_uri, RDFS.label, Literal(self._descriptions.fsn(concept.id), 'en')))

        # Generate a sctf:Description.term.$map.preferred for the preferred description for each language in LANGUAGES
        for desc in self._descriptions.synonyms(concept.id):
            for l in self._languages.preferred(desc.id):
                self.add((concept_uri, SCTF["Description.term." + l + ".preferred"],
                          Literal(desc.term, desc.languageCode)))

        # Generate a sctf:Description for the acceptable synonym for each language in LANGUAGES
        for desc in self._descriptions.synonyms(concept.id):
            for l in self._languages.acceptable(desc.id):
                self.add((concept_uri, SCTF["Description.term." + l + ".synonym"],
                          Literal(desc.term, desc.languageCode)))

        # Currently, the TextDefinition owl mapping does not support specific language variants. Add a sctf:Definition
        #  for each unique definition for each language in $LANGUAGES.
        for defn in self._descriptions.definitions(concept.id):
            if self._languages.preferred(defn.id) or self._languages.acceptable(defn.id):
                self.add((concept_uri, SCTF["TextDefinition.term"],
                          Literal(defn.term, defn.languageCode)))

        # Add an rdfs:subProperty entry for each direct parent of $concept that isn't Concept model attribute
        if typ == OWL.ObjectProperty:
            self.add_property_definition(concept, concept_uri)
        else:
            self.add_class_definition(concept, concept_uri)

    def add_property_definition(self, concept: Concept, concept_uri: URIRef) -> None:
        """
        Add a property definition
        :param concept: Concept entry for the given property
        :param concept_uri: Concept URI
        :return:
        """
        parents = [parent for parent in self._relationships.parents(concept.id)]
        if len(parents) > 1 and concept.definitionStatusId == Defined_sctid:
            target, collection = intersection(self)
            [collection.append(as_uri(parent)) for parent in parents]
            self.add((concept_uri, OWL.equivalentProperty, target))
        else:
            [self.add((concept_uri, RDFS.subPropertyOf, as_uri(parent))) for parent in parents]

        # add an owl:propertyChain assertion for $subject if is in the RIGHT_ID_LIST
        for rightid in self._context.RIGHT_IDS.get(concept.id, []):
            node = BNode()
            self.add((node, RDFS.subPropertyOf, concept_uri))
            coll = BNode()
            Collection(self, coll, [concept_uri, as_uri(rightid)])
            self.add((node, OWL.propertyChain, coll))

    def add_class_definition(self, concept: Concept, concept_uri: URIRef) -> None:
        """
        Add a class definition for the concept
        :param concept: Concept entry for the class
        :param concept_uri: Class URI
        :return:
        """
        # TODO: merge this with defining attribute
        if concept.definitionStatusId == Primitive_sctid:
            [self.add((concept_uri, RDFS.subClassOf, as_uri(parent)))
             for parent in self._relationships.parents(concept.id)]
            [self._defining_attribute(concept_uri, RDFS.subClassOf, g, members)
             for (g, members) in self._relationships.groups(concept.id).items()]

        else:
            # SNOMED assumes that every defined concept has at least one parent
            if len(self._relationships.parents(concept.id)) + len(self._relationships.groups(concept.id)) == 1:
                self.add((concept_uri, OWL.equivalentClass, list(self._relationships.parents(concept.id))[0]))
            else:
                target, coll = intersection(self)
                [coll.append(as_uri(parent)) for parent in self._relationships.parents(concept.id)]
                [self._add_defining_attribute(coll, g, members)
                 for (g, members) in self._relationships.groups(concept.id).items()]
                self.add((concept_uri, OWL.equivalentClass, target))

    def _add_defining_attribute(self, coll: Collection, group: int, rels: Set[Relationship]) -> None:
        if group == 0:
            for rel in rels:
                restr = existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId))
                if rel.typeId in self._context.NEVER_GROUPED_LIST:
                    coll.append(restr)
                else:
                    coll.append(role_group(self, restr))
        else:
            if len(rels) > 1:
                # A group whose target is an intersection of subjects + inner restrictions
                target, inner_coll = intersection(self)
                [inner_coll.append(existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId)))
                 for rel in rels]
                coll.append(role_group(self, target))
            else:
                rel = list(rels)[0]
                coll.append(existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId)))

    def _defining_attribute(self, subj: URIRef, pred: URIRef,  group: int, rels: Set[Relationship]) -> None:
        """
        A defining attribute is any active descendant of 410662002 | Concept model attribute |
        with the exception of 116680003|is a| that appears in the role of typeId in the relationship file.
        Defining attributes take one of three forms depending on whether (1) they appear in a zero (0) relationship
        group and it is not possible for them to appear in a non-zero group (2) they appear in a zero relationship
        group and it is possible for them to appear in a non-zero group and (3) they appear in non-zero relationship
         group. Each of these cases is described separately below:
        :param subj: subject of definition
        :param pred: type of definition (subClass/equivalentClass)
        :param group: relationship group
        :param rels: set of relationships in this group
        :return:
        """
        if group == 0:
            for rel in rels:
                restr = existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId))
                if rel.typeId in self._context.NEVER_GROUPED_LIST:
                    self.add((subj, pred, restr))
                else:
                    self.add((subj, pred, role_group(self, restr)))
        else:
            if len(rels) > 1:
                # A group whose target is an intersection of subjects + inner restrictions
                target, coll = intersection(self)
                [coll.append(existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId)))
                 for rel in rels]
                self.add((subj, pred, role_group(self, target)))
            else:
                rel = list(rels)[0]
                self.add((subj, pred, existential_restriction(self, as_uri(rel.typeId), as_uri(rel.destinationId))))


def main():
    g = OWLGraph(TransformationContext(open("../test/data/en_all_intl.json")),
                 directory="../test/data/Snapshot")

    # Transformation namespaces
    g.add_transformation_namespaces()

    # Ontology header
    g.add_ontology_header()

    # Add module definitions
    g.add_module_definitions()

    # Add any additional object property declarations
    g.add_object_property_declarations()

    print("Generating output")
    NAME_START_CATEGORIES.append('Nd')
    g.serialize("../test/data/output.ttl", format="turtle", encoding="utf-8")


if __name__ == '__main__':
    main()
