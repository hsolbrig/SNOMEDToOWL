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
Concept_model_object_attribute_sctid = 762705008
Concept_model_data_attribute_sctid = 762706009
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
Additional_relationship_sctid = 900000000000227009
Qualifying_relationship_scitd = 900000000000225001
Some_sctid = 900000000000451002

# SNOMED CT URIs
Role_group = SCT[str(Role_group_sctid)]

# File prefixes
ConceptFilePrefix = "sct2_Concept_Snapshot_"
DescriptionFilePrefix = "sct2_Description_Snapshot"
TextDefinitionFilePrefix = "sct2_TextDefinition_Snapshot"
LanguageFilePrefix = "der2_cRefset_LanguageSnapshot"
RelationshipFilePrefix = "sct2_Relationship_Snapshot_"
OWLRefsetFilePrefix = "sct2_sRefset_OWLExpressionSnapshot_"
ModuleDependencyFilePrefix1 = "der2_ssRefset_ModuleDependencySnapshot_"
ModuleDependencyFilePrefix2 = "def2_ssRefset_ModuleDependency_Snapshot_"


# Both IHTSDO maintained module and namespace concept sctid have children declared
# in the SNOMED Core module.  We add them and their ancestors to the "always load" branch
Module_sctid = 900000000000443000
IHTSDO_maintained_module_sctid = 900000000000445007
SDO_Maintained_module_sctid = 733981006
Namespace_concept_sctid = 370136006
Core_metadata_concept_sctid = 900000000000442005
SNOMED_CT_Model_Component_sctid = 900000000000441003

Simple_type_reference_set_sctid = 446609009
Complex_map_type_reference_set = 447250001

Foundation_metadata_concept = 900000000000454005
Reference_set = 900000000000455006
Attribute_value = 900000000000491004
Reference_set_attribute = 900000000000457003
Attribute_value_type = 900000000000480006
Concept_inactivation_value = 900000000000481005
Description_inactivation_value = 900000000000493001
Simple_map_type_reference_set = 900000000000496009
Inactive_value = 900000000000546006


AlwaysEmitOWLFor = {Module_sctid, IHTSDO_maintained_module_sctid, Namespace_concept_sctid,
                    Core_metadata_concept_sctid, SNOMED_CT_Model_Component_sctid, Simple_map_type_reference_set,
                    Complex_map_type_reference_set, Foundation_metadata_concept, Reference_set, Attribute_value,
                    Reference_set_attribute, Attribute_value_type, Concept_inactivation_value,
                    Description_inactivation_value, Simple_map_type_reference_set, Inactive_value,
                    Simple_type_reference_set_sctid, SDO_Maintained_module_sctid, Concept_model_object_attribute_sctid,
                    Concept_model_data_attribute_sctid}
