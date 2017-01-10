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
        SKOS_DESCRIPTIONS       bool        True means use skos:prefName, skos:altName, skos:definition.  False or
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
