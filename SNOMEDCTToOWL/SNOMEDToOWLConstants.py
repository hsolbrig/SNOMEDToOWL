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
from rdflib import RDF, RDFS, Namespace as RDFNamespace

#  Namespace identifiers
OWL = RDFNamespace("http://www.w3.org/2002/07/owl#")
SCTF = RDFNamespace("http://snomed.info/field/")
SCT = RDFNamespace("http://snomed.info/id/")
SCTM = RDFNamespace("http://snomed.info/sct/")

SCTID = int

required_namespaces = {"owl": OWL,
                       "rdf": RDF,
                       "rdfs": RDFS,
                       "sct": SCT,
                       "sctf": SCTF,
                       "sctm": SCTM}

# SNOMED CT Identifiers
Is_a_sctid = 116680003
Concept_model_attribute_sctid = 410662002
Linkage_concept_sctid = 106237007

Defined_sctid = 900000000000073002
Primitive_sctid = 900000000000074008

Fully_specified_name_sctid = 900000000000003001
Definition_sctid = 900000000000550004
Synonym_sctid = 900000000000013009

Preferred_sctid = 900000000000548007
Acceptable_sctid = 900000000000549004

Role_group_sctid = 609096000
Defining_relationship_sctid = 900000000000006009
Inferred_relationship_sctid = 900000000000011006
Stated_relationship_sctid = 900000000000010007
Some_sctid = 900000000000451002

# SNOMED CT URIs
Role_group = SCT[str(Role_group_sctid)]

# File prefixes
ConceptFilePrefix = "sct2_Concept_Snapshot_"
DescriptionFilePrefix = "sct2_Description_Snapshot"
TextDefinitionFilePrefix = "sct2_TextDefinition_Snapshot"
LanguageFilePrefix = "der2_cRefset_LanguageSnapshot"
StatedRelationshipFilePrefix = "sct2_StatedRelationship_Snapshot_"
RelationshipFilePrefix = "sct2_Relationship_Snapshot_"

# Both IHTSDO maintained module and namespace concept sctid have children declared
# in the SNOMED Core module.  We add them and their ancestors to the "always load" branch
Module_sctid = 900000000000443000
IHTSDO_maintained_module_sctid = 900000000000445007
Namespace_concept_sctid = 370136006
Core_metadata_concept_sctid = 900000000000442005
SNOMED_CT_Model_Component_sctid = 900000000000441003

AlwaysEmitOWLFor = {IHTSDO_maintained_module_sctid, Namespace_concept_sctid, Concept_model_attribute_sctid,
                    Core_metadata_concept_sctid, SNOMED_CT_Model_Component_sctid, Module_sctid}
