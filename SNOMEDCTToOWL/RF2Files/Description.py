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
from typing import Dict, List, Optional, Tuple

from SNOMEDCTToOWL.RF2Files import Concepts
from .RF2File import RF2File
from .Transitive import Transitive
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *
from SNOMEDCTToOWL.TransformationContext import TransformationContext


class Description:
    """ A RF2 Description or TextDefinition entry

    Properties:
        * id -- description identifier, used to link with Language file
        * conceptId -- id of concept being described
        * typeId -- description type. One of 900000000000003001 |Fully Specified Name|,
                    900000000000550004 |Definition| or 900000000000013009 |Synonym|
        * term -- description text (may contain embedded carriage returns, quotes, Latin1 encodings)
        * languageCode -- two character language code (i.e. "en", "es", ...)


    Filters:
        * active -- only active descriptions (active=='1') are included
        * moduleId --  descriptions whose moduleId's that match Transformation Context MODULE along with the FSN's of
        * descriptions whose conceptId's are  descendants of 410662002 |Concept model attribute| are used.
    """

    def __init__(self, row: Dict, is_native: bool):
        """
        Construct an RF2 description file entry
        :param row: RF2 row
        :param is_native: True means description is in target module.  False means it is added as a property.  Used to
        determine whether to emit synonyms and definitions, as native transform does not.
        """
        self.id = int(row["id"])
        self.typeId = int(row["typeId"])
        self.term = row["term"]
        self.languageCode = row["languageCode"]
        self.isNative = is_native


class Descriptions(RF2File):
    description_prefix = DescriptionFilePrefix
    textdefinition_prefix = TextDefinitionFilePrefix

    def __init__(self, concepts: Concepts):
        """
        Construct a list of term descriptions / definitions keyed by concept identifier
        """
        self._members = {}             # Dict[conceptid, Set[Description]]
        self._concepts = concepts

    @classmethod
    def filtr(cls, fname: str, _: TransformationContext) -> bool:
        """
        File name filter.
        :param fname: File name to test
        :param _:
        :return: True if file is a description/text definition file
        """
        return fname.startswith(Descriptions.description_prefix) or fname.startswith(Descriptions.textdefinition_prefix)

    def add(self, row: Dict, context: TransformationContext, transitive: Transitive) -> None:
        """
        Add RF2 description file row if belongs to the target module or is a FSN for a property.  Note, however, that
        FSN's are added so they can be supplied if the concept itself is used (i.e. has one or more descriptions or
        definitions supplied by the target module)
        :param row: row to add -- already tested for active
        :param context: transformation context
        :param transitive: Transitive relationships
        """
        conceptid = int(row['conceptId'])
        if int(row['moduleId']) == context.MODULE or \
                transitive.is_descendant_or_self_of(conceptid, Concept_model_attribute_sctid) or \
                int(row['typeId']) == Fully_specified_name_sctid:
            self._members.setdefault(conceptid, set()).add(Description(row, int(row['moduleId']) == context.MODULE))
        if int(row['moduleId']) == context.MODULE or conceptid in AlwaysEmitOWLFor:
            self._concepts.add_concept_id(conceptid)

    def fsn(self, conceptid: SCTID, context: TransformationContext) -> Tuple[str, str]:
        """
        Return the fully specified name for conceptid
        :param conceptid: sctid
        :param context: transformation context
        :return: FSN / language code
        """
        fsns = [desc for desc in self._members[conceptid] if desc.typeId == Fully_specified_name_sctid]
        # Single FSN always passes
        if len(fsns) == 1:
            fsn_idx = 0
            return fsns[0].term, fsns[0].languageCode

        # No FSN is badly formed
        elif len(fsns) == 0:
            raise Exception("No FSN specified for conceptid {}".format(conceptid))

        # Pass the first language code that matches a target language ("en" matches "en-us" as an example)
        for fsn in fsns:
            for lang_code in context.LANGUAGE_MAP.values():
                if lang_code.startswith(fsn.languageCode):
                    return fsn.term, fsn.languageCode

        # Return the english fsn
        for fsn in fsns:
            if fsn.languageCode == 'en':
                return fsn.term, fsn.languageCode

        # Return a random fsn
        return fsns[0].term, fsns[0].languageCode


    def synonyms(self, conceptid: SCTID) -> List[Description]:
        """
        Return the synonyms for conceptid
        :param conceptid: sctid
        :return: list of synonyms, if any
        """
        return [desc for desc in self._members[conceptid] if desc.typeId == Synonym_sctid]

    def definitions(self, conceptid: SCTID) -> List[Description]:
        """
        Return the text definitions for conceptid
        :param conceptid: sctid
        :return: list of definitions if any
        """
        return [defn for defn in self._members[conceptid] if defn.typeId == Definition_sctid]
