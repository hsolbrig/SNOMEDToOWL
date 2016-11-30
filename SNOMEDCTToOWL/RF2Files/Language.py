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
from typing import Dict, List

from .RF2File import RF2File
from .Transitive import Transitive
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *
from SNOMEDCTToOWL.TransformationContext import TransformationContext

LanguageName = str


class Language:
    """ A RF2 Language refset entry

    Properties:
        * refsetId -- specific language identifier
        * acceptabilityId -- acceptability in the context of the language.  900000000000548007 |Preferred| or
          900000000000549004 |Acceptable|
        * referencedComponentId -- description or text definition identifier

    Filters:
        * active -- only active language entries (active=='1') are included
        * moduleId -- language entry moduleId must match Transformation Context MODULE
        * refsetId -- only refsets in Transformation Context LANGUAGES list match
        *
    """

    def __init__(self, row: Dict, context: TransformationContext):
        """
        A language entry in the RF2 language file.  Consists of a language *name* and acceptability id
        :param row: RF2 language file row
        :param context: transformation context
        """
        self.lang = context.LANGUAGE_MAP[int(row['refsetId'])]
        self.acceptabilityId = int(row["acceptabilityId"])


class Languages(RF2File):
    prefix = LanguageFilePrefix

    def __init__(self):
        """
        Collection of language refsets for concepts
        """
        self._members = {}          # Dict[referencedComponentId, Set[LanguageName]]

    def add(self, row: Dict, context: TransformationContext, _: Transitive) -> None:
        """
        Add a language entry if needed
        :param row: row to add -- already tested for active
        :param context: transformation context
        :param _: Unused
        """
        if int(row['moduleId']) == context.MODULE and int(row['refsetId']) in context.LANGUAGES:
            self._members.setdefault(int(row['referencedComponentId']), set()).add(Language(row, context))

    def preferred(self, descid: SCTID) -> List[LanguageName]:
        """
        Return the preferred language identifiers for descid
        :param descid: description identifier
        :return: list of specific languages that descid is preferred for
        """
        return self._filter_langs(descid, Preferred_sctid)

    def acceptable(self, descid: SCTID) -> List[LanguageName]:
        """
        Return the acceptable language entries for descid
        :param descid: description identifier
        :return: list of specific languages that descid is acceptable for
        """
        return self._filter_langs(descid, Acceptable_sctid)

    def _filter_langs(self, entryid: SCTID, acceptability: SCTID) -> List[LanguageName]:
        """
        Return the language name for the supplied description/definition id and acceptability filter
        :param entryid: description or definition row id
        :param acceptability: return type
        :return: list of language names that apply to this id and accepability
        """
        return [lang.lang for lang in self._members.get(entryid, []) if lang.acceptabilityId == acceptability]
