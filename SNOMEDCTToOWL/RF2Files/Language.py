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
