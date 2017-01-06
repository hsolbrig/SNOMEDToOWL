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
import os
import sys
from typing import Dict
from argparse import ArgumentParser, Namespace

from SNOMEDCTToOWL.RF2Files.DirectoryWalker import DirectoryWalker
from SNOMEDCTToOWL.RF2Files.Transitive import Transitive
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *

AlwaysLoad = {Is_a_sctid, Concept_model_attribute_sctid, Linkage_concept_sctid, Defined_sctid,
              Primitive_sctid, Fully_specified_name_sctid, Definition_sctid, Synonym_sctid, Module_sctid,
              Preferred_sctid, Acceptable_sctid, Role_group_sctid, Defining_relationship_sctid, Some_sctid,
              Inferred_relationship_sctid, Stated_relationship_sctid, IHTSDO_maintained_module_sctid,
              Namespace_concept_sctid, Core_metadata_concept_sctid, SNOMED_CT_Model_Component_sctid}


class RF2Filter:
    def __init__(self, opts: Namespace):
        """
        Construct an RF2 Filter context

        """
        self._opts = opts                       # user options

        self._matched_concepts = set()          # List of matched concepts -- used to report conceptid's not found
        self._visited_concepts = set()          # Concepts that have already been seen
        self._visited_descriptions = set()      # Descriptions that have already been seen

        self._walker = DirectoryWalker(opts.indir, opts.outdir, opts.init)

        print("Build transitive closure list")
        self._transitive = Transitive()
        self._process_transitive()              # Compute transitive closure list
        AlwaysLoad.update(self._transitive.descendants_of(Concept_model_attribute_sctid))

        print("Filtering files")
        self._process_relationships()           # Pass over requested concepts adding
        print("Adding {} concepts".format(len(self._visited_concepts)))
        self._process_concepts()                # Copy all visited concept entries
        self._process_descriptions()            # ... their descriptions
        self._process_textdefinitions()         # ... their definitions
        self._process_languages()               # ... and the corresponding language entries

    @property
    def matches(self):
        return self._matched_concepts

    def _process_transitive(self) -> None:
        """
        Walk through the relationship file building the transitive closures
        :return:
        """
        self._walker.walk(lambda file: file.startswith(RelationshipFilePrefix),
                          lambda row: self._proc_transitive_row(row))

    def _proc_transitive_row(self, row) -> bool:
        """
        Add IS_A relationships to the transitive file
        :param row:
        :return: False -- nothing is added to output at this point
        """
        if int(row['active']) == 1 and int(row['typeId']) == Is_a_sctid:
            self._transitive.add(row)
        return False

    def _process_relationships(self) -> None:
        """
        Iteratively all relationship entries whose subject is in the required concepts
        """
        self._visited_concepts.update(self._opts.conceptid)
        if self._opts.ancestors:
            for cid in self._opts.conceptid:
                self._visited_concepts.update(self._transitive.ancestors_of(cid))
        if self._opts.descendants:
            for cid in self._opts.conceptid:
                self._visited_concepts.update(self._transitive.descendants_of(cid))
        self._visited_concepts.update(AlwaysLoad)

        iteration = 1
        while True:
            num_entries = len(self._visited_concepts)
            self._walker.walk(lambda file: file.startswith(RelationshipFilePrefix) or
                                           file.startswith(StatedRelationshipFilePrefix),
                              lambda row: self._proc_relationship_row(row))
            if not (self._opts.ancestors or self._opts.descendants) or len(self._visited_concepts) == num_entries:
                break
            print("Iteration {}: {} new concepts".format(iteration, len(self._visited_concepts) - num_entries))
            iteration += 1

    def _proc_relationship_row(self, row: Dict) -> bool:
        """
        Return true if the sourceId of row is in the list of concepts to process
        :param row: relationship row
        :return:
        """
        sourceid = int(row['sourceId'])
        destinationid = int(row['destinationId'])
        typeid = int(row['typeId'])
        if self._opts.children and not self._opts.descendants and \
           destinationid in self._opts.conceptid and typeid == Is_a_sctid:
               self._visited_concepts.add(sourceid)
        if sourceid in self._visited_concepts:
            self._visited_concepts.add(destinationid),
            self._visited_concepts.add(typeid)
            return True
        return False

    def _process_concepts(self) -> None:
        self._walker.walk(lambda file: file.startswith(ConceptFilePrefix),
                          lambda row: self._proc_concept_row(row))

    def _proc_concept_row(self, row: Dict) -> bool:
        conceptid = int(row['id'])
        if conceptid in self._opts.conceptid or conceptid in AlwaysLoad:
            self._matched_concepts.add(conceptid)
            return True
        return conceptid in self._visited_concepts

    def _process_descriptions(self):
        self._walker.walk(lambda file: file.startswith(DescriptionFilePrefix),
                          lambda row: self._proc_description_row(row))

    def _proc_description_row(self, row: Dict) -> bool:
        conceptid = int(row['conceptId'])
        if conceptid in self._opts.conceptid or conceptid in AlwaysLoad or \
                (conceptid in self._visited_concepts and int(row['typeId']) == Fully_specified_name_sctid):
            self._visited_descriptions.add(int(row['id']))
            return True
        return False

    def _process_textdefinitions(self):
        self._walker.walk(lambda file: file.startswith(TextDefinitionFilePrefix),
                          lambda row: self._proc_definition_row(row))

    def _proc_definition_row(self, row: Dict) -> bool:
        conceptid = int(row['conceptId'])
        if conceptid in self._opts.conceptid:
            self._visited_descriptions.add(int(row['id']))
            return True
        return False

    def _process_languages(self):
        self._walker.walk(lambda file: file.startswith(LanguageFilePrefix),
                          lambda row: int(row['referencedComponentId']) in self._visited_descriptions)


def genargs() -> ArgumentParser:
    parser = ArgumentParser(description="Extract selected SNOMED-CT RF2 concepts")
    parser.add_argument("indir", help="Location of existing RF2 Snapshot directory")
    parser.add_argument("outdir", help="Target directory for filtered RF2 content")
    parser.add_argument("conceptid", help="List of concept identifiers to extract", nargs="*", type=int)
    parser.add_argument("-i", "--init", help="Initialize the target output files", action="store_true")
    parser.add_argument("-a", "--ancestors", help="Add touched concept ancestors", action="store_true")
    parser.add_argument("-c", "--children", help="Add direct children of selected concepts", action="store_true")
    parser.add_argument("-d", "--descendants", help="Add children, children of children, etc of selected concepts",
                        action="store_true")

    return parser


def main(argv):
    opts = genargs().parse_args(argv)
    if opts.indir == opts.outdir:
        print("Input directory (%s) cannot match output directory ($s)" % opts.indir, opts.outdir, file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(opts.indir):
        print("Cannot open input directory (%s)" % opts.indir, file=sys.stderr)
        sys.exit(1)

    generated = RF2Filter(opts).matches
    for c in set(opts.conceptid) - generated:
        print("*** CONCEPT: %s not found ***", str(c))
