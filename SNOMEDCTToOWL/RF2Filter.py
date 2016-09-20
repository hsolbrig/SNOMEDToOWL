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
import sys
from typing import Callable, Dict
from argparse import ArgumentParser, Namespace

from SNOMEDCTToOWL.RF2Files.Transitive import Transitive
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *

AlwaysLoad = {Is_a_sctid, Concept_model_attribute_sctid, Linkage_concept_sctid, Defined_sctid,
              Primitive_sctid, Fully_specified_name_sctid, Definition_sctid, Synonym_sctid,
              Preferred_sctid, Acceptable_sctid, Role_group_sctid, Defining_relationship_sctid, Some_sctid,
              Inferred_relationship_sctid, Stated_relationship_sctid}


class RF2DictWriter(csv.DictWriter):
    """
    DictWriter wrapper with "with" idiom to close the output file
    """
    def __init__(self, f, *args, **argv):
        self._f = f
        csv.DictWriter.__init__(self, f, *args, **argv)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._f.close()


class DirectoryWalker:
    def __init__(self, indir: str, outdir, init: bool):
        """
        Directory walking utility
        :param indir: directory root to walk from
        :param outdir: output directory root to walk to
        :param init: If true, remove existing content in output files
        """
        self._indir = indir
        self._outdir = outdir
        self._init = init

    def walk(self, filtr: Callable[[str], bool], processor: Callable[[Dict], bool]) -> None:
        """
        Walk the directory testing the file against filtr and invoking processor with contents if true
        :param filtr: file name tester
        :param processor: content row processor
        """
        for filedir, _, files in os.walk(self._indir):
            for file in files:
                if filtr(file):
                    print("Processing %s" % os.path.join(filedir, file))
                    with open(os.path.join(filedir, file)) as f:
                        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                        with self._create_writer(filedir, file, reader) as writer:
                            for row in reader:
                                if processor(row):
                                    writer.writerow(row)

    def _create_writer(self, filedir, file, inreader: csv.DictReader) -> RF2DictWriter:
        outdir = filedir.replace(self._indir, self._outdir)
        os.makedirs(outdir, exist_ok=True)
        output_file = os.path.join(filedir.replace(self._indir, self._outdir), file)
        is_new = self._init or not os.path.exists(output_file)
        writer = RF2DictWriter(open(output_file, 'w' if is_new else 'a'),
                               fieldnames=inreader.fieldnames, dialect=csv.excel_tab)
        if is_new:
            writer.writeheader()
        return writer


class RF2Filter:
    def __init__(self, opts: Namespace):
        """
        Construct an RF2 Filter context

        """
        self._opts = opts
        self._transitive = Transitive()
        self._matched_concepts = set()
        self._visited_concepts = set()
        self._visited_descriptions = set()

        self._walker = DirectoryWalker(opts.indir, opts.outdir, opts.init)

        print("Build transitive closure")
        self._process_transitive()
        AlwaysLoad.update(self._transitive.descendants_of(Concept_model_attribute_sctid))
        print("Filtering files")
        self._process_relationships()
        self._process_concepts()
        self._process_descriptions()
        self._process_textdefinitions()
        self._process_languages()

    @property
    def matches(self):
        return self._matched_concepts

    def _process_transitive(self) -> None:
        self._walker.walk(lambda file: file.startswith(RelationshipFilePrefix),
                          lambda row: self._proc_transitive_row(row))

    def _proc_transitive_row(self, row):
        if int(row['active']) == 1 and int(row['typeId']) == Is_a_sctid:
            self._transitive.add(row)
        return False        # Don't add anything to the output files now

    def _process_relationships(self) -> None:
        self._walker.walk(lambda file: file.startswith(RelationshipFilePrefix) or
                                       file.startswith(StatedRelationshipFilePrefix),
                          lambda row: self._proc_relationship_row(row))

    def _proc_relationship_row(self, row: Dict) -> bool:
        sourceid = int(row['sourceId'])
        destinationid = int(row['destinationId'])
        typeid = int(row['typeId'])
        if sourceid in self._opts.concepts or sourceid in AlwaysLoad:
            self._visited_concepts.add(sourceid)
            self._visited_concepts.add(destinationid),
            self._visited_concepts.add(typeid)
            return True
        return False

    def _process_concepts(self) -> None:
        self._walker.walk(lambda file: file.startswith(ConceptFilePrefix),
                          lambda row: self._proc_concept_row(row))

    def _proc_concept_row(self, row: Dict) -> bool:
        conceptid = int(row['id'])
        if conceptid in self._opts.concepts or conceptid in AlwaysLoad:
            self._matched_concepts.add(conceptid)
            return True
        return conceptid in self._visited_concepts

    def _process_descriptions(self):
        self._walker.walk(lambda file: file.startswith(DescriptionFilePrefix),
                          lambda row: self._proc_description_row(row))

    def _proc_description_row(self, row: Dict) -> bool:
        conceptid = int(row['conceptId'])
        if conceptid in self._opts.concepts or conceptid in AlwaysLoad or \
                (conceptid in self._visited_concepts and int(row['typeId']) == Fully_specified_name_sctid):
            self._visited_descriptions.add(int(row['id']))
            return True
        return False

    def _process_textdefinitions(self):
        self._walker.walk(lambda file: file.startswith(TextDefinitionFilePrefix),
                          lambda row: self._proc_definition_row(row))

    def _proc_definition_row(self, row: Dict) -> bool:
        conceptid = int(row['conceptId'])
        if conceptid in self._opts.concepts:
            self._visited_descriptions.add(int(row['id']))
            return True
        return False

    def _process_languages(self):
        self._walker.walk(lambda file: file.startswith(LanguageFilePrefix),
                          lambda row: int(row['referencedComponentId']) in self._visited_descriptions)


def genargs() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("indir", help="Input directory")
    parser.add_argument("outdir", help="Output directory")
    parser.add_argument("-i", "--init", help="Initialize the target output files", action="store_true")
    parser.add_argument("-c", "--concepts", help="List of concepts to add", nargs="+", type=int, required=True)
    return parser


def main():
    opts = genargs().parse_args()
    if opts.indir == opts.outdir:
        print("Input directory (%s) cannot match output directory ($s)" % opts.indir, opts.outdir, file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(opts.indir):
        print("Cannot open input directory (%s)" % opts.indir, file=sys.stderr)
        sys.exit(1)

    generated = RF2Filter(opts).matches
    for c in set(opts.concepts) - generated:
        print("*** CONCEPT: %s not found ***", str(c))


if __name__ == '__main__':
    main()
