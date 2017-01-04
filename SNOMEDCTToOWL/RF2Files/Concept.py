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
from typing import Dict, Union

from .RF2File import RF2File
from .Transitive import Transitive
from SNOMEDCTToOWL.TransformationContext import TransformationContext
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *


class Concept:
    """ A RF2 Concept entry

    Properties:
        * id  -- concept identifier. Used to form the subject IRI
        * definitionStatusId -- determines whether the OWL definition uses owl:equivalentClass / owl:equivalentProperty
            (900000000000073002 |Defined|) rdfs:subClassOf / owl:subPropertyOf 900000000000074008 |Primitive|.

    Filters:
        active -- only active concepts (active=='1') are included
        moduleId --  concepts whose moduleId's that match Transformation Context MODULE and either:
        (a) Are not descendants of 160237007 |Linkage concept| or
        (b) are also descendants of 410662002 |Concept model attribute| are included.
        All (active) descendants of 410662002 |Concept model attribute| are also included whether the module matches or
         not, but are minimally represented in the output
    """
    def __init__(self, row_or_id: Union[Dict, int]):
        """
        Construct a representative of an RF2 concept row
        :param row_or_id: RF2 concept file row or concept identifier
        """
        if isinstance(row_or_id, dict):
            self.id = int(row_or_id['id'])
            self.definitionStatusId = int(row_or_id["definitionStatusId"])
        else:
            self.id = row_or_id
            self.definitionStatusId = Primitive_sctid


class Concepts(RF2File):
    prefix = ConceptFilePrefix

    def __init__(self):
        """
        Construct a list of qualifying concepts
        """
        self.all_active_concepts = set()
        self.properties = dict()        # Non-member properties: Dict[conceptid, Concept]
        self.members = dict()           # Member properties or classes:  Dict[conceptid, Concept]
        self.added_concepts = set()    # Concepts not in module, but having added descriptions or definitions: Set[int]

    def add(self, row: Dict, context: TransformationContext, transitive: Transitive) -> None:
        """
        Add an RF2 concept row to the list of concepts
        :param row: row to add -- already tested for active in RF2File
        :param context: context with modules, filters, etc
        :param transitive: transitive closure file
        """
        conceptid = int(row['id'])
        self.all_active_concepts.add(conceptid)
        if int(row['moduleId']) == context.MODULE and\
                not transitive.is_descendant_of(conceptid, Linkage_concept_sctid):
            self.members[conceptid] = Concept(row)
        elif transitive.is_descendant_of(conceptid, Concept_model_attribute_sctid):
            self.properties[conceptid] = Concept(row)

    def add_concept_id(self, conceptid: int) -> None:
        """
        Add conceptid to members.  Used for descriptions whose concepts aren't in the target module
        :param conceptid: concept to add
        :return:
        """
        if conceptid in self.all_active_concepts and conceptid not in self.members and conceptid not in self.properties:
            self.added_concepts.add(conceptid)
