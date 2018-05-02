from io import TextIOWrapper
from jsonasobj import load


class TransformationContext:
    """
    A Transformation Context consists of:
        Element                 Type        Description
        --------                ----------  -----------
        MODULE                  int         SCTID of the module being transformed to owl
        VERSION                 int         VERSION identifier of particular release or extension
        VERSION_DESCRIPTION     str         A description of the version
        LANGUAGES               List[int]   A list of language refset SCTIDS
        LANGUAGE_MAP            Map[int, str] A map from a language refset to an english language description
        MODULE_LABEL            str         The label of the module/ontology
        MODULE_DESCRIPTION      str         A description of the module
        MODULE_COPYRIGHT        str         The module copyright
        NEVER_GROUPED           List[int]   A list of SCTIDS that never occur inside relationship groups
        RIGHT_ID                Map[int, List[int]]
        USE_STATED_RELATIONSHIPS bool       True or absent means use the stated relationships, else use inferred
        SKOS_DESCRIPTIONS       bool        True means use skos:prefLabel, skos:altLabel, skos:definition.  False or
                                            absent means use SNOMED predicates
    """
    def __init__(self, context_config: TextIOWrapper):
        ctxt = load(context_config)
        self.MODULE = ctxt.MODULE
        self.VERSION = ctxt.VERSION
        self.VERSION_DESCRIPTION = self.multi_line(ctxt.VERSION_DESCRIPTION)
        self.LANGUAGES = ctxt.LANGUAGES
        self.LANGUAGE_MAP = {int(k): v for k, v in ctxt.LANGUAGE_MAP._as_dict.items()}
        self.MODULE_LABEL = ctxt.MODULE_LABEL
        self.MODULE_DESCRIPTION = self.multi_line(ctxt.MODULE_DESCRIPTION)
        self.MODULE_COPYRIGHT = self.multi_line(ctxt.MODULE_COPYRIGHT)
        self.NEVER_GROUPED = ctxt.NEVER_GROUPED
        self.RIGHT_ID = {int(k): v for k, v in ctxt.RIGHT_ID._as_dict.items()}
        self.USE_STATED_RELATIONSHIPS = ctxt._as_dict.get("USE_STATED_RELATIONSHIPS", True)
        self.SKOS_DESCRIPTIONS = ctxt._as_dict.get("SKOS_DESCRIPTIONS", False)

    @staticmethod
    def multi_line(txt):
        return '\n'.join(txt) if isinstance(txt, list) else txt
